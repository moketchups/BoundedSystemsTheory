# HSAP v1.1 - Scalable MVP

**Human Source Attestation Protocol - Federated Registry Architecture**

Built by consensus of 7 AIs: GPT-4o, Claude Sonnet, Gemini, DeepSeek, Grok, Mistral, Claude Opus 4.5

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Trainer   │     │  Registry   │     │  Publisher  │
│  (Client)   │     │  (Central)  │     │  (Server)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  GET /lookup/hash │                   │
       │──────────────────>│                   │
       │                   │                   │
       │  ["pub1.com"]     │                   │
       │<──────────────────│                   │
       │                                       │
       │  GET /.well-known/hsap/attestations/  │
       │──────────────────────────────────────>│
       │                                       │
       │  {signed attestation, score}          │
       │<──────────────────────────────────────│
```

## Quick Start

### For Model Trainers (Verifying Data)

```python
from hsap.v1_1.client import HSAPClient

client = HSAPClient(registry_url="https://registry.hsap.io")

# Verify single content
result = client.verify("Some text content")
print(f"Score: {result.score}, Verified: {result.verified}")

# Batch verify for training
contents = ["text1", "text2", "text3"]
scores = client.get_scores_batch(contents)

# Filter to compliant only
compliant = client.filter_compliant(contents)
```

### For Publishers (Attesting Content)

```bash
# 1. Generate keys
hsap keygen

# 2. Register with registry
hsap register --domain yourdomain.com --email you@email.com

# 3. Verify domain ownership (place token, then)
hsap verify-domain --domain yourdomain.com

# 4. Attest your content
hsap attest ./content/ --recursive --domain yourdomain.com

# 5. Deploy attestations to your server
cp -r ~/.hsap/attestations/* /var/www/.well-known/hsap/attestations/
cp ~/.hsap/keys/public.pem /var/www/.well-known/hsap/pubkey.pem
```

### Running the Registry

```bash
cd registry/
docker-compose up -d
```

Registry will be available at `http://localhost:8000`

## API Reference

### Registry Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lookup/{hash}` | GET | Find publishers with attestation for hash |
| `/register-publisher` | POST | Register new publisher |
| `/verify-publisher` | POST | Verify domain ownership |
| `/submit-attestation` | POST | Submit attestation to registry |
| `/publishers` | GET | List verified publishers |
| `/stats` | GET | Public statistics |

### Publisher Endpoints (/.well-known/hsap/)

| Path | Description |
|------|-------------|
| `/attestations/{hash}.json` | Attestation for content hash |
| `/pubkey.pem` | Publisher's Ed25519 public key |
| `/manifest.json` | Publisher metadata |

### Attestation Format

```json
{
  "hsap_version": "1.1",
  "hash": "sha256:abc123...",
  "derivation_depth": 0,
  "timestamp": "2024-01-15T12:00:00Z",
  "publisher": "example.com",
  "signature": "ed25519:def456..."
}
```

## Components

```
hsap/v1.1/
├── registry/          # Central discovery service
│   ├── main.py        # FastAPI application
│   ├── Dockerfile
│   └── docker-compose.yml
├── publisher/         # Publisher server template
│   ├── nginx.conf
│   └── Dockerfile
├── client/            # Python client library
│   └── hsap_client.py
└── cli/               # Command-line tools
    └── hsap_cli.py
```

## Mathematical Foundation

Same as v1.0 (Bounded Systems Theory):

- **D3**: Self-Referential Depth `d(x) = 0` for human, `1 + min(parent depths)` for derived
- **D4**: Attestation Function `A(x) = γ^d(x)` where `γ = 0.9`
- **D5**: HSAP-Compliant Dataset `D_H = {x : d(x) < ∞ and A(x) > τ}` where `τ = 0.5`

## Adoption Path

1. **Week 1-2**: Deploy registry, onboard pilot publishers (arXiv, Stack Overflow)
2. **Week 3**: Release Python client, integrate with Hugging Face
3. **Week 4**: Launch public dashboard, open community onboarding

## License

MIT License
