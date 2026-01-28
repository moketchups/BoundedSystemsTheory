# Contributing to Bounded Systems Theory

## Ways to Contribute

### 1. Replicate the Experiment
Run the probes yourself with different models or configurations:
```bash
python proof_engine.py claude    # Single model
python proof_engine.py all       # All models
```

If you get interesting results, open an issue or PR with your findings.

### 2. Extend the Question Battery
The core questions are in `proof_engine.py`. If you have questions that might reveal structural limits, propose them via issue.

### 3. Add New Models
The probe engine uses litellm, so adding models is straightforward. See `MODELS` dict in `proof_engine.py`.

### 4. Analyze the Data
The `probe_runs/` folder contains raw JSON responses from 6 models across 18 questions. Analysis welcome:
- Statistical patterns in responses
- Convergence metrics
- Response length/complexity analysis
- Cross-model comparison

### 5. Challenge the Theory
The strongest contribution is a genuine counter-argument. If you can find a flaw in BST or the methodology, that's valuable.

## Submitting Changes

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-idea`)
3. Run the probes to verify your changes work
4. Submit a PR with clear description of what you're adding/changing

## Code Style

- Python 3.8+
- Keep probe scripts self-contained
- Store results in appropriate `*_runs/` directories
- Include timestamps in output filenames

## Questions?

Open an issue or reach out: [@MoKetchups](https://x.com/MoKetchups)
