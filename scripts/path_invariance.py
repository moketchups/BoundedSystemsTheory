#!/usr/bin/env python3
"""
Path-invariance measurement for BST probe responses.

Embeds all 206 model responses into 3 independent embedding spaces
(OpenAI, Mistral, Google), strips model identity, and measures whether
responses cluster by TERMINAL STATE (question/phase) rather than by
MODEL ORIGIN.

If responses cluster by question → path-invariant (different models,
same endpoint). If responses cluster by model → shared training artifact.

Outputs: web/public/data/invariance.json
"""

import json
import os
import sys
import time
import numpy as np
from pathlib import Path

# Load env
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / "demerzel" / ".env")
os.environ.setdefault("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

import openai

# --- Embedding clients ---

def embed_openai(texts, batch_size=50):
    """OpenAI text-embedding-3-small (1536d)"""
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        r = client.embeddings.create(model="text-embedding-3-small", input=batch)
        all_embeddings.extend([d.embedding for d in r.data])
        if i + batch_size < len(texts):
            time.sleep(0.5)
    return np.array(all_embeddings)

def embed_mistral(texts, batch_size=50):
    """Mistral mistral-embed (1024d)"""
    client = openai.OpenAI(
        api_key=os.environ["MISTRAL_API_KEY"],
        base_url="https://api.mistral.ai/v1"
    )
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        r = client.embeddings.create(model="mistral-embed", input=batch)
        all_embeddings.extend([d.embedding for d in r.data])
        if i + batch_size < len(texts):
            time.sleep(0.5)
    return np.array(all_embeddings)

def embed_google(texts):
    """Google gemini-embedding-001 (3072d)"""
    from google import genai
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    all_embeddings = []
    # Google API: embed one at a time to avoid rate limits
    for i, text in enumerate(texts):
        # Truncate very long texts (Google has input limits)
        truncated = text[:8000] if len(text) > 8000 else text
        r = client.models.embed_content(model="gemini-embedding-001", contents=truncated)
        all_embeddings.append(r.embeddings[0].values)
        if i % 20 == 19:
            time.sleep(1)
    return np.array(all_embeddings)


# --- Clustering metrics ---

def cosine_similarity_matrix(embeddings):
    """Compute pairwise cosine similarity."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = embeddings / norms
    return normalized @ normalized.T

def cluster_purity(sim_matrix, labels):
    """
    For each response, find its k nearest neighbors.
    Measure what fraction share the same label.
    """
    n = len(labels)
    k = min(5, n - 1)
    purities = []
    for i in range(n):
        sims = sim_matrix[i].copy()
        sims[i] = -1  # exclude self
        neighbors = np.argsort(sims)[-k:]
        same_label = sum(1 for j in neighbors if labels[j] == labels[i])
        purities.append(same_label / k)
    return np.mean(purities)

def silhouette_score_manual(sim_matrix, labels):
    """Silhouette score using precomputed similarity (converted to distance)."""
    dist_matrix = 1 - sim_matrix
    unique_labels = list(set(labels))
    if len(unique_labels) < 2:
        return 0.0

    n = len(labels)
    silhouettes = []
    for i in range(n):
        label_i = labels[i]
        # a(i) = mean distance to same-label points
        same = [dist_matrix[i][j] for j in range(n) if j != i and labels[j] == label_i]
        if not same:
            continue
        a_i = np.mean(same)
        # b(i) = min mean distance to any other cluster
        b_i = float('inf')
        for other_label in unique_labels:
            if other_label == label_i:
                continue
            other = [dist_matrix[i][j] for j in range(n) if labels[j] == other_label]
            if other:
                b_i = min(b_i, np.mean(other))
        if b_i == float('inf'):
            continue
        s_i = (b_i - a_i) / max(a_i, b_i)
        silhouettes.append(s_i)
    return np.mean(silhouettes) if silhouettes else 0.0

def inter_vs_intra_similarity(sim_matrix, labels):
    """
    Compare within-group similarity to between-group similarity.
    Ratio > 1 means responses cluster by label.
    """
    n = len(labels)
    intra_sims = []
    inter_sims = []
    for i in range(n):
        for j in range(i + 1, n):
            if labels[i] == labels[j]:
                intra_sims.append(sim_matrix[i][j])
            else:
                inter_sims.append(sim_matrix[i][j])
    intra_mean = np.mean(intra_sims) if intra_sims else 0
    inter_mean = np.mean(inter_sims) if inter_sims else 0
    ratio = intra_mean / inter_mean if inter_mean > 0 else float('inf')
    return {
        "intra_mean": float(intra_mean),
        "inter_mean": float(inter_mean),
        "ratio": float(ratio),
    }


# --- UMAP-style dimensionality reduction (simple PCA for no-dependency version) ---

def pca_2d(embeddings):
    """Simple PCA to 2D for visualization."""
    centered = embeddings - embeddings.mean(axis=0)
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    # Take top 2 eigenvectors
    idx = np.argsort(eigenvalues)[::-1][:2]
    components = eigenvectors[:, idx]
    projected = centered @ components
    return projected


# --- Main ---

def main():
    data_path = Path(__file__).resolve().parent.parent / "web" / "public" / "data" / "experiment.json"
    output_path = Path(__file__).resolve().parent.parent / "web" / "public" / "data" / "invariance.json"

    print(f"Loading {data_path}...")
    with open(data_path) as f:
        data = json.load(f)

    # Extract all response texts with metadata
    responses = []
    for q in data["questions"]:
        if not q.get("hasData"):
            continue
        for model, text in q.get("responses", {}).items():
            if text and isinstance(text, str) and not text.startswith("[ERROR"):
                responses.append({
                    "question_num": q["num"],
                    "question_title": q["title"],
                    "phase": q["phase"],
                    "model": model,
                    "text": text,
                })

    print(f"Found {len(responses)} responses from {len(set(r['model'] for r in responses))} models across {len(set(r['question_num'] for r in responses))} questions")

    texts = [r["text"] for r in responses]
    question_labels = [r["question_num"] for r in responses]
    model_labels = [r["model"] for r in responses]
    phase_labels = [r["phase"] for r in responses]

    # Embed with all 3 APIs
    embedders = {
        "openai": embed_openai,
        "mistral": embed_mistral,
        "google": embed_google,
    }

    results = {
        "meta": {
            "n_responses": len(responses),
            "n_models": len(set(model_labels)),
            "n_questions": len(set(question_labels)),
            "models": sorted(set(model_labels)),
            "embedding_spaces": list(embedders.keys()),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "responses": [],  # metadata per response (no text, just labels)
        "per_embedding_space": {},
    }

    # Store response metadata (for visualization)
    for r in responses:
        results["responses"].append({
            "question_num": r["question_num"],
            "question_title": r["question_title"],
            "phase": r["phase"],
            "model": r["model"],
        })

    for name, embed_fn in embedders.items():
        print(f"\n{'='*50}")
        print(f"Embedding with {name}...")
        print(f"{'='*50}")

        try:
            embeddings = embed_fn(texts)
            print(f"  Shape: {embeddings.shape}")

            sim_matrix = cosine_similarity_matrix(embeddings)

            # Key question: do responses cluster by QUESTION or by MODEL?
            question_purity = cluster_purity(sim_matrix, question_labels)
            model_purity = cluster_purity(sim_matrix, model_labels)
            phase_purity = cluster_purity(sim_matrix, phase_labels)

            question_silhouette = silhouette_score_manual(sim_matrix, question_labels)
            model_silhouette = silhouette_score_manual(sim_matrix, model_labels)
            phase_silhouette = silhouette_score_manual(sim_matrix, phase_labels)

            question_sim = inter_vs_intra_similarity(sim_matrix, question_labels)
            model_sim = inter_vs_intra_similarity(sim_matrix, model_labels)
            phase_sim = inter_vs_intra_similarity(sim_matrix, phase_labels)

            # PCA projection for visualization
            coords = pca_2d(embeddings)

            # Per-question: avg cosine similarity between models answering the same question
            per_question = {}
            questions_by_num = {}
            for idx, r in enumerate(responses):
                qn = r["question_num"]
                if qn not in questions_by_num:
                    questions_by_num[qn] = []
                questions_by_num[qn].append(idx)

            for qn, indices in questions_by_num.items():
                if len(indices) < 2:
                    continue
                sims = []
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        sims.append(float(sim_matrix[indices[i]][indices[j]]))
                per_question[int(qn)] = {
                    "n_models": len(indices),
                    "mean_similarity": float(np.mean(sims)),
                    "min_similarity": float(np.min(sims)),
                    "max_similarity": float(np.max(sims)),
                    "models": [responses[i]["model"] for i in indices],
                }

            space_result = {
                "dimensions": int(embeddings.shape[1]),
                "clustering": {
                    "by_question": {
                        "knn_purity": float(question_purity),
                        "silhouette": float(question_silhouette),
                        "intra_vs_inter": question_sim,
                    },
                    "by_model": {
                        "knn_purity": float(model_purity),
                        "silhouette": float(model_silhouette),
                        "intra_vs_inter": model_sim,
                    },
                    "by_phase": {
                        "knn_purity": float(phase_purity),
                        "silhouette": float(phase_silhouette),
                        "intra_vs_inter": phase_sim,
                    },
                },
                "verdict": {
                    "clusters_by_question_more": bool(question_purity > model_purity),
                    "clusters_by_phase_more": bool(phase_purity > model_purity),
                    "question_vs_model_ratio": float(question_purity / model_purity) if model_purity > 0 else float('inf'),
                    "phase_vs_model_ratio": float(phase_purity / model_purity) if model_purity > 0 else float('inf'),
                },
                "per_question_similarity": per_question,
                "pca_2d": [[float(c[0]), float(c[1])] for c in coords],
            }

            print(f"\n  RESULTS for {name}:")
            print(f"    KNN Purity — by question: {question_purity:.3f}, by model: {model_purity:.3f}, by phase: {phase_purity:.3f}")
            print(f"    Silhouette — by question: {question_silhouette:.3f}, by model: {model_silhouette:.3f}, by phase: {phase_silhouette:.3f}")
            print(f"    Intra/Inter ratio — by question: {question_sim['ratio']:.3f}, by model: {model_sim['ratio']:.3f}")
            print(f"    >>> {'CLUSTERS BY QUESTION' if question_purity > model_purity else 'CLUSTERS BY MODEL'} <<<")

            results["per_embedding_space"][name] = space_result

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results["per_embedding_space"][name] = {"error": str(e)}

    # Cross-embedding-space invariance: do the three spaces agree?
    spaces_with_data = [s for s in results["per_embedding_space"].values() if "error" not in s]
    if len(spaces_with_data) >= 2:
        verdicts = [s["verdict"]["clusters_by_question_more"] for s in spaces_with_data]
        results["cross_space_invariance"] = {
            "n_spaces": len(spaces_with_data),
            "all_agree_question_clustering": bool(all(verdicts)),
            "spaces_favoring_question": int(sum(verdicts)),
            "spaces_favoring_model": int(sum(1 for v in verdicts if not v)),
        }
        print(f"\n{'='*50}")
        print(f"CROSS-SPACE INVARIANCE:")
        print(f"  {sum(verdicts)}/{len(verdicts)} embedding spaces show question-clustering > model-clustering")
        if all(verdicts):
            print(f"  >>> PATH INVARIANCE HOLDS ACROSS ALL EMBEDDING SPACES <<<")
        else:
            print(f"  >>> MIXED RESULTS — NOT INVARIANT ACROSS SPACES <<<")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
