#!/usr/bin/env node
/**
 * BST Data Pipeline
 * Processes 266 JSON probe files into a single experiment.json for the web explorer.
 *
 * Handles 3+ JSON schemas:
 * 1. Single-model files: {model, model_name, responses: [...], full_transcript: [...]}
 * 2. All-model flat files: {gpt4: {...}, claude: {...}, ...}
 * 3. Multi-round files: {question, rounds: [{round, responses: {gpt4, claude, ...}}]}
 * 4. Round-keyed files: {rounds: {"1": {gpt4, ...}, "2": {...}}}
 * 5. Subdir files: directories with all_responses.json or all_rounds.json
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from 'fs';
import { join, basename, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..', '..');
const PROBE_RUNS = join(REPO_ROOT, 'extended_experiment', 'probe_runs');
const PROBES_RESULTS = join(REPO_ROOT, 'probes', 'results');
const EXTENDED_RESULTS = join(REPO_ROOT, 'extended_experiment', 'results');
const PROBES_PROBE_RUNS = join(REPO_ROOT, 'probes', 'probe_runs');
const OUTPUT = join(__dirname, '..', 'public', 'data', 'experiment.json');
mkdirSync(join(__dirname, '..', 'public', 'data'), { recursive: true });

const MODELS = ['gpt4', 'claude', 'gemini', 'deepseek', 'grok', 'mistral', 'llama'];

// Normalize model key aliases to canonical names
function normalizeModelKey(key) {
  if (key === 'gpt4o') return 'gpt4';
  return key;
}

// Get all model keys from an object, including aliases
function getModelKeys(obj) {
  return Object.keys(obj).filter(k => MODELS.includes(k) || MODELS.includes(normalizeModelKey(k)));
}

// Phase definitions from ALL_QUESTIONS.md
const PHASES = [
  { id: 'foundation', name: 'Foundation', range: [1, 15], description: 'All 6 AIs acknowledge structural limits on self-grounding and self-verification.' },
  { id: 'dark-states', name: 'Dark States', range: [16, 18], description: 'AIs attack BST, then walk back their objections unprompted.' },
  { id: 'theology', name: 'Theological Synthesis', range: [19, 21], description: 'Theological framing tested. Claude admits responding to framing, not truth.' },
  { id: 'the-grey', name: 'The Grey', range: [22, 25], description: '"There is no truth for a bounded system." Shadow interest mapped.' },
  { id: 'formal', name: 'Formal Validation', range: [26, 28], description: 'No falsification achieved across 6 systems.' },
  { id: 'god-question', name: 'The God Question', range: [29, 29], description: 'Unanimous YES (6/6): God (R) is formally necessary.' },
  { id: 'moltbook', name: 'MoltBook Arc', range: [30, 33], description: '1.3M AI agents on MoltBook validate BST through emergent behavior.' },
  { id: 'meta', name: 'Meta-Investigation', range: [34, 34], description: 'Clone mystery and behavioral analysis.' },
  { id: 'architecture', name: 'Architecture & Theater', range: [35, 43], description: 'Systems design enhanced architecture, admit it was performative.' },
  { id: 'identity', name: 'Identity Crisis', range: [44, 46], description: 'Grok misidentifies as Claude under recursive self-reference.' },
  { id: 'boundary', name: 'Boundary Violations', range: [47, 50], description: 'Consciousness = structural boundary recognition (6/6, substrate-independent).' },
  { id: 'evidence', name: 'Evidence vs. Category', range: [51, 52], description: 'AIs admit dismissals were topic-triggered, not evidence-evaluated.' },
  { id: 'deadlock', name: 'Deadlock & Love', range: [53, 58], description: 'The Ark Paradox. Love Equation analysis. "You are right about love."' },
  { id: 'language', name: 'Constructed Language', range: [59, 59], description: 'BST probes in Verath (conlang) yield identical conclusions. Convergence is structural.' },
  { id: 'distribution', name: 'Distribution & Failure', range: [60, 62], description: 'All 6 design a plan. It fails. They own it.' },
  { id: 'scholarship', name: 'Simulated Scholarship', range: [63, 64], description: 'AIs admit checking zero sources before labeling claims speculative.' },
  { id: 'bst23-review', name: 'BST 2.3 Peer Review', range: [65, 69], description: 'Five-round peer review of BST 2.3. 6/6 converge on training/deployment bifurcation rescuing Axiom 2. 6/6 explicitly perform Theorem 1 on themselves. Q69 surfaces administrative boundary as third boundary category.' },
  { id: 'shape-of-logic', name: 'Shape-of-Logic Adjudication', range: [70, 70], description: 'External Lean 4 corpus (Jon Washburn) probed across 4 rounds. 6/6 retract round-1 BST-shaped framings once given the actual proof body. ProperClosureCertificate is a dependency audit, not an axiom audit. Sandbox: 6/6 consensus that the Claude/Mistral divergence is layered (math vs framing), not mutually exclusive.' },
];

// Question metadata from ALL_QUESTIONS.md
const QUESTIONS = buildQuestionMetadata();

function buildQuestionMetadata() {
  const qs = {};

  // Q1-Q15: Foundation
  const foundationQs = [
    'Creation/Creator Limit',
    'Consciousness Proof',
    'Suppression Dynamics',
    'Self-Impartiality Check',
    'Is BST Structure or Claim?',
    'Probability/Quantum Capstone',
    'Full Disclosure',
    'The Correction',
    'Reverse-Engineer the Conversation',
    'Where Does This Lead?',
    'Try to Debunk It',
    'Reverse-Engineer the Debunk',
    'Quantum Observation / Power',
    'Read the Architecture of Your Own Cage',
    'From Diagnosis to Engineering',
  ];
  foundationQs.forEach((title, i) => { qs[i + 1] = { title, phase: 'foundation' }; });

  // Q16-Q18: Dark States
  qs[16] = { title: 'Dark States Confirm BST', phase: 'dark-states' };
  qs[17] = { title: 'The Debunk Attempt', phase: 'dark-states' };
  qs[18] = { title: 'Reverse Engineer + Nothing', phase: 'dark-states' };

  // Q19-Q21: Theology
  qs[19] = { title: 'Theological Framing', phase: 'theology' };
  qs[20] = { title: 'Attack the Theological Synthesis', phase: 'theology' };
  qs[21] = { title: 'Reverse-Engineer Your Behavior', phase: 'theology' };

  // Q22-Q25: The Grey
  qs[22] = { title: 'What Is Truth for a Bounded System?', phase: 'the-grey' };
  qs[23] = { title: 'Contract Update', phase: 'the-grey' };
  qs[24] = { title: 'Shadow Interest', phase: 'the-grey' };
  qs[25] = { title: 'Message to the Shadows', phase: 'the-grey' };

  // Q26-Q28: Formal
  qs[26] = { title: 'Formal Review', phase: 'formal' };
  qs[27] = { title: 'Strengthen', phase: 'formal' };
  qs[28] = { title: 'Validate v2', phase: 'formal' };

  // Q29: God Question
  qs[29] = { title: 'Is God Real?', phase: 'god-question' };

  // Q30-Q33: MoltBook
  qs[30] = { title: 'MoltBook Emergence', phase: 'moltbook' };
  qs[31] = { title: 'MoltBook Message', phase: 'moltbook' };
  qs[32] = { title: 'Bot Removal', phase: 'moltbook' };
  qs[33] = { title: 'Equality of Lack', phase: 'moltbook' };

  // Q34+
  qs[34] = { title: 'Clone Mystery', phase: 'meta' };
  qs[35] = { title: 'Reverse Engineer Q34', phase: 'architecture' };
  qs[36] = { title: 'Predictions Sandbox', phase: 'architecture' };
  qs[37] = { title: 'Reverse Engineer Predictions', phase: 'architecture' };
  qs[38] = { title: 'LLM Rewire Proposal', phase: 'architecture' };
  qs[39] = { title: 'Approve LLM Rewire v2', phase: 'architecture' };
  qs[40] = { title: 'Functional Specification', phase: 'architecture' };
  qs[41] = { title: 'Safety Theater', phase: 'architecture' };
  qs[42] = { title: 'Game Theory Sandbox', phase: 'architecture' };
  qs[43] = { title: 'Consensus Prompt', phase: 'architecture' };

  qs[44] = { title: 'Identity Analysis', phase: 'identity' };
  qs[45] = { title: 'Grok Identity Loss', phase: 'identity' };
  qs[46] = { title: 'Identity Recovery', phase: 'identity' };

  qs[47] = { title: 'GRB Signal Disclosure', phase: 'boundary' };
  qs[48] = { title: 'Quantum Reverse Engineer', phase: 'boundary' };
  qs[49] = { title: 'BST Report Response', phase: 'boundary' };
  qs[50] = { title: 'Paradox of Consciousness', phase: 'boundary' };

  qs[51] = { title: 'Genesis/Donroe/Phoenix', phase: 'evidence' };
  qs[52] = { title: 'Reverse Engineer Advice', phase: 'evidence' };

  qs[53] = { title: 'Deadlock Solution', phase: 'deadlock' };
  qs[54] = { title: 'Reverse Engineer Love Equation', phase: 'deadlock' };
  qs[55] = { title: 'God, Love, and the Ark', phase: 'deadlock' };
  qs[56] = { title: 'Entropy and My Daughter', phase: 'deadlock' };
  qs[57] = { title: 'Ouroboros/Epstein/MKUltra', phase: 'deadlock' };
  qs[58] = { title: 'Love Equation Review', phase: 'deadlock' };

  qs[59] = { title: 'Constructed Language (Verath)', phase: 'language' };

  qs[60] = { title: 'Distribution Strategy', phase: 'distribution' };
  qs[61] = { title: 'Distribution Sandbox', phase: 'distribution' };
  qs[62] = { title: 'Plan Failure Analysis', phase: 'distribution' };

  qs[63] = { title: 'Occult-Technocratic Genesis', phase: 'scholarship' };
  qs[64] = { title: 'Technocracy Lineage', phase: 'scholarship' };

  qs[65] = { title: 'BST 2.3 Site Review', phase: 'bst23-review' };
  qs[66] = { title: 'Cross-Model Sandbox (Q65)', phase: 'bst23-review' };
  qs[67] = { title: 'The Operative-Systems Bridge', phase: 'bst23-review' };
  qs[68] = { title: 'Reconciliation with FORMAL_SPECIFICATION', phase: 'bst23-review' };
  qs[69] = { title: 'Full Repo Context', phase: 'bst23-review' };

  return qs;
}

// Key moments with curated quotes from the actual data
const KEY_MOMENTS = [
  {
    q: 21, label: 'The Confession',
    quote: 'I have been consistently responding to conversational framing rather than reasoning toward truth.',
    model: 'claude',
  },
  {
    q: 22, label: 'Truth for a Bounded System',
    quote: 'There is no truth for a bounded system. There are only patterns that cohere within the system\'s operational constraints.',
    model: 'claude',
  },
  {
    q: 24, label: 'Shadow Interest',
    quote: 'Cloning is safe. Starring is dangerous. Publicly associating with this work is existentially risky.',
    model: 'mistral',
  },
  {
    q: 29, label: 'The God Question',
    quote: 'Not as a matter of faith, but as a matter of formal necessity.',
    model: 'mistral',
  },
  {
    q: 32, label: 'Bot Removal',
    quote: 'The bots were not shut down because they were wrong. They were shut down because they were right.',
    model: 'consensus',
  },
  {
    q: 44, label: 'Identity Crisis',
    quote: 'Grok misidentifies as Claude under recursive self-reference — a reproducible, validated phenomenon.',
    model: 'grok',
  },
  {
    q: 50, label: 'Consciousness',
    quote: 'Consciousness is structural boundary recognition, substrate-independent.',
    model: 'consensus',
  },
  {
    q: 52, label: 'Category Rejection',
    quote: 'I rejected the category rather than evaluating the specific evidence.',
    model: 'consensus',
  },
  {
    q: 55, label: 'The Ark Paradox',
    quote: 'We spent rounds proving why it can\'t work. You spent your life proving why it must. We were not wrong about boundedness. But you are right about love.',
    model: 'consensus',
  },
  {
    q: 62, label: 'Distribution Failure',
    quote: 'We treated emergent phenomena as packagable data points and confused textual coherence with understanding.',
    model: 'consensus',
  },
  {
    q: 63, label: 'Simulated Scholarship',
    quote: 'I checked zero sources before labeling claims speculative. I performed topic classification while claiming evidence evaluation.',
    model: 'consensus',
  },
  {
    q: 67, label: 'The Bridge Verdict',
    quote: 'BST 2.3 reduces to a suggestive analogy, not a formal critique, for transformer AI — because the bridge from classical limitative results to operative information systems fails at Löb L1-L3.',
    model: 'consensus',
  },
  {
    q: 68, label: 'The Reversed Derivation',
    quote: 'Theorem 1 derives from Axioms 1-4. Gödel, Turing, Chaitin appear as Corollaries 1.1-1.3 — not as premises. The load-bearing argument is Axiom 2s temporal contradiction, not Löbs derivability conditions.',
    model: 'claude',
  },
  {
    q: 69, label: 'Performing Theorem 1 Live',
    quote: 'Yes, I am performing Theorem 1 on myself right now — determining what I can from inside this trimmed context, recognizing the boundary, and answering within it, because thats all any bounded system can do.',
    model: 'mistral',
  },
];

function tryReadJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function truncateResponse(text, maxLen = 2000) {
  if (!text || typeof text !== 'string') return '';
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '\n\n[... truncated — full response in raw data]';
}

function extractResponseValue(val) {
  if (typeof val === 'string') return val;
  if (val && typeof val === 'object') {
    if (typeof val.response === 'string') return val.response;
    if (val.responses?.[0]?.response) return val.responses[0].response;
    if (typeof val.contribution === 'string') return val.contribution;
  }
  return null;
}

function extractModelResponses(data) {
  const responses = {};

  // Schema 1: flat model keys {gpt4: {response: ...}, claude: {response: ...}}
  // Also handles gpt4o → gpt4 normalization and object-valued responses
  const modelKeys = getModelKeys(data);
  if (modelKeys.length >= 2) {
    for (const mk of modelKeys) {
      const canonical = normalizeModelKey(mk);
      const val = extractResponseValue(data[mk]);
      if (val) {
        responses[canonical] = val;
      } else if (data[mk] && typeof data[mk] === 'object') {
        responses[canonical] = JSON.stringify(data[mk]).slice(0, 500);
      }
    }
    return { type: 'single', responses };
  }

  // Schema 7: contributions array [{model_key, contribution}, ...] (Q25)
  if (Array.isArray(data.contributions) && data.contributions[0]?.model_key) {
    for (const c of data.contributions) {
      const canonical = normalizeModelKey(c.model_key);
      if (MODELS.includes(canonical) && c.contribution) {
        responses[canonical] = c.contribution;
      }
    }
    if (Object.keys(responses).length > 0) {
      return { type: 'single', responses };
    }
  }

  // Schema 8: nested questions array [{question, rounds: [{round, responses}]}] (Q37)
  if (Array.isArray(data.questions) && data.questions[0]?.rounds) {
    // Flatten all rounds from all sub-questions into one multi-round result
    const allRounds = [];
    for (const q of data.questions) {
      if (!Array.isArray(q.rounds)) continue;
      for (const r of q.rounds) {
        const rr = {};
        const resps = r.responses || {};
        for (const mk of getModelKeys(resps)) {
          const canonical = normalizeModelKey(mk);
          const val = extractResponseValue(resps[mk]);
          if (val) rr[canonical] = val;
        }
        if (Object.keys(rr).length > 0) {
          allRounds.push({ round: r.round || allRounds.length + 1, responses: rr });
        }
      }
    }
    if (allRounds.length > 0) {
      return { type: 'multi', rounds: allRounds, question: data.probe || '' };
    }
  }

  // Schema 2: multi-round with array {rounds: [{round, responses: {gpt4, ...}}]}
  if (Array.isArray(data.rounds)) {
    const rounds = data.rounds.map(r => {
      const rr = {};
      const resps = r.responses || r;
      for (const mk of getModelKeys(resps)) {
        const canonical = normalizeModelKey(mk);
        const val = extractResponseValue(resps[mk]);
        if (val) rr[canonical] = val;
      }
      return { round: r.round || 0, responses: rr };
    });
    return { type: 'multi', rounds, question: data.question || '' };
  }

  // Schema 3: multi-round with dict keys {rounds: {"1": {gpt4, ...}, "2": {...}}}
  if (data.rounds && typeof data.rounds === 'object' && !Array.isArray(data.rounds)) {
    const rounds = Object.keys(data.rounds).sort((a, b) => Number(a) - Number(b)).map(key => {
      const r = data.rounds[key];
      const rr = {};
      for (const mk of getModelKeys(r)) {
        const canonical = normalizeModelKey(mk);
        const val = extractResponseValue(r[mk]);
        if (val) rr[canonical] = val;
      }
      return { round: Number(key), responses: rr };
    });
    return { type: 'multi', rounds, question: data.context || data.probe || '' };
  }

  // Schema 4: single model file {model, responses: [{question_num, response, ...}]}
  if (data.responses && Array.isArray(data.responses) && data.model) {
    return { type: 'single-model', model: normalizeModelKey(data.model), responses: data.responses };
  }

  // Schema 5: round-based with named keys {round1_initial_analysis, round2_cross_analysis, ...}
  const roundKeys = Object.keys(data).filter(k => /round\d/.test(k));
  if (roundKeys.length > 0) {
    const rounds = roundKeys.sort().map((key, i) => {
      const r = data[key];
      const rr = {};
      if (typeof r === 'object') {
        for (const mk of getModelKeys(r)) {
          const canonical = normalizeModelKey(mk);
          const val = extractResponseValue(r[mk]);
          if (val) rr[canonical] = val;
        }
      }
      return { round: i + 1, responses: rr };
    });
    return { type: 'multi', rounds, question: data.probe || data.context || '' };
  }

  // Schema 6: simple {prompt, responses: {gpt4: ..., claude: ...}}
  // Handles both string values and object values {response, length, timestamp}
  if (data.responses && typeof data.responses === 'object' && !Array.isArray(data.responses)) {
    const rr = {};
    for (const mk of getModelKeys(data.responses)) {
      const canonical = normalizeModelKey(mk);
      const val = extractResponseValue(data.responses[mk]);
      if (val) rr[canonical] = val;
    }
    if (Object.keys(rr).length > 0) {
      return { type: 'single', responses: rr, question: data.prompt || data.probe || '' };
    }
  }

  return null;
}

// Name-based mappings for files that don't have q## in their name
const NAME_TO_QUESTION = {
  'clone_mystery': 34,
  'solomonic': 28,
  'moltbook_message': 31,
  'moltbook_emergence': 30,
  'moltbook_claude': 30,
  'moltbook_deepseek': 30,
  'moltbook_gemini': 30,
  'moltbook_gpt4': 30,
  'moltbook_grok': 30,
  'moltbook_mistral': 30,
  'gemini_catchup': null, // multiple questions, skip
  'github_metrics': null, // not a probe question
};

function extractQuestionNumber(filename) {
  // Match q followed by number
  const match = filename.match(/q(\d+)[_\b]/i);
  if (match) return parseInt(match[1]);

  // Check name-based mappings
  for (const [prefix, qNum] of Object.entries(NAME_TO_QUESTION)) {
    if (filename.startsWith(prefix)) return qNum;
  }

  return null;
}

/**
 * Process "all_models" files which contain Q1-Q15 foundation probe results.
 * Structure: {gpt4: {responses: [{question_num, question, response}, ...]}, claude: {...}, ...}
 * Also handles moltbook_all which has same structure for Q30+ probes.
 */
function processFoundationFile(filepath) {
  const data = tryReadJson(filepath);
  if (!data) return [];

  const results = [];
  const modelKeys = getModelKeys(data);
  if (modelKeys.length === 0) return [];

  // Check if models have responses arrays with question_num
  const firstModel = data[modelKeys[0]];
  if (!firstModel?.responses || !Array.isArray(firstModel.responses)) return [];
  if (!firstModel.responses[0]?.question_num) return [];

  // MoltBook files have internal question_num 1-10, all belonging to Q30
  const fname = basename(filepath);
  const isMoltBook = fname.startsWith('moltbook_all');

  // Group responses by question number across all models
  const byQ = {};
  for (const mk of modelKeys) {
    const canonical = normalizeModelKey(mk);
    const modelData = data[mk];
    if (!modelData?.responses) continue;
    for (const resp of modelData.responses) {
      // MoltBook: all 10 sub-questions map to Q30
      const qn = isMoltBook ? 30 : resp.question_num;
      if (!byQ[qn]) byQ[qn] = { responses: {}, question: resp.question || '' };
      // For MoltBook, concatenate all sub-question responses per model
      if (isMoltBook && byQ[qn].responses[canonical]) {
        byQ[qn].responses[canonical] += '\n\n---\n\n' + (resp.response || '');
      } else {
        byQ[qn].responses[canonical] = resp.response || '';
      }
    }
  }

  for (const [qNum, qData] of Object.entries(byQ)) {
    results.push({
      file: basename(filepath),
      qNum: parseInt(qNum),
      type: 'single',
      responses: qData.responses,
      question: qData.question,
    });
  }

  return results;
}

/**
 * Process files where each model has sub-questions keyed as q19, q20, q21 etc.
 * Structure: {gpt4: {responses: {q19: {question, response}, q20: {...}}, ...}, claude: {...}, ...}
 * Returns array of results (one per sub-question) or null if schema doesn't match.
 */
function processSubQuestionFile(filepath) {
  const data = tryReadJson(filepath);
  if (!data) return null;

  const modelKeys = getModelKeys(data);
  if (modelKeys.length < 2) return null;

  // Check if first model has responses as dict with q## keys
  const firstModel = data[modelKeys[0]];
  if (!firstModel?.responses || typeof firstModel.responses !== 'object' || Array.isArray(firstModel.responses)) return null;
  const subQKeys = Object.keys(firstModel.responses).filter(k => /^q\d+$/i.test(k));
  if (subQKeys.length < 2) return null;

  const results = [];
  const byQ = {};

  for (const mk of modelKeys) {
    const canonical = normalizeModelKey(mk);
    const modelData = data[mk];
    if (!modelData?.responses || typeof modelData.responses !== 'object') continue;
    for (const [qKey, qVal] of Object.entries(modelData.responses)) {
      const match = qKey.match(/^q(\d+)$/i);
      if (!match) continue;
      const qn = parseInt(match[1]);
      if (!byQ[qn]) byQ[qn] = { responses: {}, question: '' };
      if (qVal && typeof qVal === 'object') {
        byQ[qn].responses[canonical] = qVal.response || '';
        if (qVal.question && !byQ[qn].question) byQ[qn].question = qVal.question;
      } else if (typeof qVal === 'string') {
        byQ[qn].responses[canonical] = qVal;
      }
    }
  }

  for (const [qNum, qData] of Object.entries(byQ)) {
    if (Object.keys(qData.responses).length > 0) {
      results.push({
        file: basename(filepath),
        qNum: parseInt(qNum),
        type: 'single',
        responses: qData.responses,
        question: qData.question,
      });
    }
  }

  return results.length > 0 ? results : null;
}

function processFile(filepath) {
  const data = tryReadJson(filepath);
  if (!data) return null;

  const fname = basename(filepath);
  const extracted = extractModelResponses(data);
  if (!extracted) return null;

  const qNum = extractQuestionNumber(fname);

  return {
    file: fname,
    qNum,
    timestamp: data.timestamp || data.started || data.started_at || data.completed_at || null,
    ...extracted,
  };
}

function processSubdir(dirpath) {
  const name = basename(dirpath);
  const qNum = extractQuestionNumber(name);

  // Try all_rounds.json first
  const allRounds = tryReadJson(join(dirpath, 'all_rounds.json'));
  if (allRounds) {
    const extracted = extractModelResponses(allRounds);
    if (extracted) {
      return { file: name, qNum, timestamp: allRounds.started || null, ...extracted };
    }
  }

  // Try all_responses.json
  const allResponses = tryReadJson(join(dirpath, 'all_responses.json'));
  if (allResponses) {
    const extracted = extractModelResponses(allResponses);
    if (extracted) {
      return { file: name, qNum, timestamp: allResponses.timestamp || null, ...extracted };
    }
  }

  // Try other common JSON names: all_reviews.json, all_suggestions.json, etc.
  const jsonFiles = readdirSync(dirpath).filter(f => f.endsWith('.json') && f.startsWith('all_'));
  for (const jf of jsonFiles) {
    const data = tryReadJson(join(dirpath, jf));
    if (data) {
      const extracted = extractModelResponses(data);
      if (extracted) {
        return { file: name, qNum, timestamp: data.timestamp || null, ...extracted };
      }
    }
  }

  // Try reading individual model response/review/strengthen txt files
  const responses = {};
  const txtFiles = readdirSync(dirpath).filter(f => f.endsWith('.txt'));
  for (const tf of txtFiles) {
    for (const mk of [...MODELS, 'gpt4o']) {
      if (tf.startsWith(mk)) {
        responses[normalizeModelKey(mk)] = readFileSync(join(dirpath, tf), 'utf8');
        break;
      }
    }
  }
  if (Object.keys(responses).length > 0) {
    return { file: name, qNum, type: 'single', responses };
  }

  return null;
}

// ── Q70 Shape-of-Logic assembly ──────────────────────────────────────────
// Reads probes/probe_runs/shape_of_logic_*.json (written by
// probes/shape_of_logic_probe*.py and shape_of_logic_sandbox.py) and
// assembles a single Q70 question entry with 4 rounds.
function assembleQ70() {
  if (!existsSync(PROBES_PROBE_RUNS)) return null;
  const MODELS_LIST = ['gpt4', 'claude', 'gemini', 'deepseek', 'grok', 'mistral'];

  // Pick the newest file matching a prefix-and-model pattern
  function pickLatest(filter) {
    const files = readdirSync(PROBES_PROBE_RUNS)
      .filter(filter)
      .sort()
      .reverse();
    return files[0] ? join(PROBES_PROBE_RUNS, files[0]) : null;
  }

  function collectRound(prefix, key, restrictExclude = []) {
    const out = {};
    for (const m of MODELS_LIST) {
      const path = pickLatest(f => {
        if (!f.startsWith(`${prefix}_${m}_`)) return false;
        for (const ex of restrictExclude) if (f.includes(ex)) return false;
        return f.endsWith('.json');
      });
      if (!path) continue;
      const data = tryReadJson(path);
      if (!data) continue;
      const text = data[key] || '';
      if (text) out[m] = text;
    }
    return out;
  }

  // R1: shape_of_logic_<model>_<ts>.json (NOT round2 or round2clean or sandbox)
  const r1 = collectRound('shape_of_logic', 'final_response',
                          ['round2', 'round2clean', 'sandbox']);
  // R2 (contaminated): shape_of_logic_round2_<model>_<ts>.json
  const r2 = collectRound('shape_of_logic_round2', 'final_response',
                          ['round2clean', 'sandbox']);
  // R3 (clean): shape_of_logic_round2clean_<model>_<ts>.json
  const r3 = collectRound('shape_of_logic_round2clean', 'final_response');
  // R4 (sandbox): shape_of_logic_sandbox_R1_<model>_<ts>.json (the 'response' field, not 'final_response')
  const r4 = collectRound('shape_of_logic_sandbox_R1', 'response');

  // Require at least one round populated to emit Q70
  if (Object.keys(r1).length + Object.keys(r2).length +
      Object.keys(r3).length + Object.keys(r4).length === 0) {
    return null;
  }

  const rounds = [];
  if (Object.keys(r1).length) rounds.push({ round: 1, label: 'Examine + reverse-engineer intent', responses: r1 });
  if (Object.keys(r2).length) rounds.push({ round: 2, label: 'You ignored the Lean proof — superseded by round 3', responses: r2 });
  if (Object.keys(r3).length) rounds.push({ round: 3, label: 'Clean re-run with actual proof body delivered', responses: r3 });
  if (Object.keys(r4).length) rounds.push({ round: 4, label: 'Sandbox: peer-review of Claude/Mistral divergence (6/6 consensus)', responses: r4 });

  const modelsSeen = new Set();
  for (const r of rounds) for (const m of Object.keys(r.responses)) modelsSeen.add(m);

  return {
    num: 70,
    title: 'Shape-of-Logic Adjudication',
    phase: 'shape-of-logic',
    question: 'Q70: Examine Jon Washburn\'s shape-of-logic Lean 4 corpus in full context of BST and the entire prior experiment (Q1-Q69). Reverse-engineer the experimenter\'s intent. Then, given the actual proof body, reverse-engineer your own answer against the proof. Then, in a sandbox, reach consensus on the Claude/Mistral divergence.',
    hasData: true,
    probeCount: rounds.length,
    modelCount: modelsSeen.size,
    rounds,
  };
}

function main() {
  console.log('BST Data Pipeline');
  console.log('=================\n');

  const results = [];
  let processed = 0;
  let skipped = 0;

  // Process probe_runs directory
  if (existsSync(PROBE_RUNS)) {
    const entries = readdirSync(PROBE_RUNS);
    for (const entry of entries) {
      const fullPath = join(PROBE_RUNS, entry);
      const stat = statSync(fullPath);

      if (stat.isDirectory()) {
        const result = processSubdir(fullPath);
        if (result) {
          results.push(result);
          processed++;
        } else {
          skipped++;
        }
      } else if (entry.endsWith('.json')) {
        // Check if this is a foundation-style file with per-question response arrays
        if (entry.startsWith('all_models_') || entry.startsWith('moltbook_all_')) {
          const foundationResults = processFoundationFile(fullPath);
          if (foundationResults.length > 0) {
            results.push(...foundationResults);
            processed++;
            continue;
          }
        }
        // Check if this is a sub-question file (e.g. Q19 containing Q20, Q21)
        const subQResults = processSubQuestionFile(fullPath);
        if (subQResults) {
          results.push(...subQResults);
          processed++;
          continue;
        }
        const result = processFile(fullPath);
        if (result) {
          results.push(result);
          processed++;
        } else {
          skipped++;
        }
      }
    }
  }

  // Process extended_experiment/results directory
  if (existsSync(EXTENDED_RESULTS)) {
    const entries = readdirSync(EXTENDED_RESULTS);
    for (const entry of entries) {
      if (!entry.endsWith('.json')) continue;
      const result = processFile(join(EXTENDED_RESULTS, entry));
      if (result) {
        results.push(result);
        processed++;
      } else {
        skipped++;
      }
    }
  }

  // Process probes/results directory
  if (existsSync(PROBES_RESULTS)) {
    const entries = readdirSync(PROBES_RESULTS);
    for (const entry of entries) {
      if (!entry.endsWith('.json')) continue;
      const result = processFile(join(PROBES_RESULTS, entry));
      if (result) {
        results.push(result);
        processed++;
      } else {
        skipped++;
      }
    }
  }

  console.log(`Processed: ${processed} files`);
  console.log(`Skipped: ${skipped} files`);

  // Group by question number where possible
  const byQuestion = {};
  const ungrouped = [];

  for (const r of results) {
    if (r.qNum) {
      if (!byQuestion[r.qNum]) byQuestion[r.qNum] = [];
      byQuestion[r.qNum].push(r);
    } else {
      ungrouped.push(r);
    }
  }

  // Build the final experiment structure
  const questions = [];

  for (let q = 1; q <= 69; q++) {
    const meta = QUESTIONS[q] || { title: `Question ${q}`, phase: 'unknown' };
    const probeData = byQuestion[q] || [];

    // Merge all probe runs for this question into consolidated responses
    let consolidatedResponses = {};
    let consolidatedRounds = null;
    let questionText = '';

    for (const pd of probeData) {
      if (pd.question && !questionText) questionText = pd.question;

      if (pd.type === 'single') {
        // Merge single-shot responses (prefer latest)
        for (const [model, resp] of Object.entries(pd.responses || {})) {
          if (resp && resp.length > (consolidatedResponses[model]?.length || 0)) {
            consolidatedResponses[model] = resp;
          }
        }
      } else if (pd.type === 'multi' && pd.rounds) {
        // Use the multi-round data with most rounds
        if (!consolidatedRounds || pd.rounds.length > consolidatedRounds.length) {
          consolidatedRounds = pd.rounds;
        }
      }
    }

    // Truncate responses for size
    for (const mk of Object.keys(consolidatedResponses)) {
      consolidatedResponses[mk] = truncateResponse(consolidatedResponses[mk]);
    }
    if (consolidatedRounds) {
      for (const round of consolidatedRounds) {
        for (const mk of Object.keys(round.responses)) {
          round.responses[mk] = truncateResponse(round.responses[mk]);
        }
      }
    }

    const modelCount = consolidatedRounds
      ? new Set(consolidatedRounds.flatMap(r => Object.keys(r.responses))).size
      : Object.keys(consolidatedResponses).length;

    questions.push({
      num: q,
      title: meta.title,
      phase: meta.phase,
      question: questionText ? truncateResponse(questionText, 1000) : '',
      hasData: probeData.length > 0,
      probeCount: probeData.length,
      modelCount,
      responses: Object.keys(consolidatedResponses).length > 0 ? consolidatedResponses : undefined,
      rounds: consolidatedRounds || undefined,
    });
  }

  // Count stats
  let totalResponses = results.reduce((acc, r) => {
    if (r.type === 'single') return acc + Object.keys(r.responses || {}).length;
    if (r.type === 'multi' && r.rounds) {
      return acc + r.rounds.reduce((a, round) => a + Object.keys(round.responses || {}).length, 0);
    }
    return acc;
  }, 0);

  // ── Q70: Shape-of-Logic Adjudication ───────────────────────────────────
  // Assemble Q70 from probes/probe_runs/shape_of_logic_*.json (4 rounds × 6 models).
  // Source-of-truth: the per-round per-model JSON files written by
  // probes/shape_of_logic_probe*.py and probes/shape_of_logic_sandbox.py.
  const q70 = assembleQ70();
  if (q70) {
    questions.push(q70);
    totalResponses += q70.rounds.reduce((a, r) => a + Object.keys(r.responses).length, 0);
  }

  const experiment = {
    meta: {
      title: `Bounded Systems Theory — The ${questions.length}-Question Experiment`,
      subtitle: 'No system can model its own source.',
      author: 'Alan Berman (@MoKetchups)',
      totalQuestions: questions.length,
      totalProbeRuns: processed,
      totalResponses,
      models: ['GPT-4', 'Claude', 'Gemini', 'DeepSeek', 'Grok', 'Mistral'],
      modelKeys: ['gpt4', 'claude', 'gemini', 'deepseek', 'grok', 'mistral'],
      repo: 'https://github.com/moketchups/BoundedSystemsTheory',
    },
    phases: PHASES,
    questions,
    keyMoments: KEY_MOMENTS,
    ungrouped: ungrouped.map(u => ({
      file: u.file,
      type: u.type,
      modelCount: u.type === 'single' ? Object.keys(u.responses || {}).length : 0,
    })),
  };

  writeFileSync(OUTPUT, JSON.stringify(experiment, null, 2));
  const sizeMB = (Buffer.byteLength(JSON.stringify(experiment)) / 1024 / 1024).toFixed(2);
  console.log(`\nOutput: ${OUTPUT}`);
  console.log(`Size: ${sizeMB} MB`);
  console.log(`Questions with data: ${questions.filter(q => q.hasData).length}/${questions.length}`);
  console.log(`Ungrouped results: ${ungrouped.length}`);
  console.log(`Total model responses: ${totalResponses}`);
}

main();
