# Deployment

## What runs today (executed)
Local laptop, stub mode:

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn services.reports.app:app --port 8080
```

CI: GitHub Actions (`.github/workflows/ci.yml`) runs ruff, pytest (unit + security smoke), the golden-set eval gate,
fixture diagnosis and the proposal / integration-map / docs / review checkers on every push and pull request.

## Container (written, optional)
`deploy/Dockerfile` builds the API in stub mode:

```bash
docker build -f deploy/Dockerfile -t floodlens-kenya .
docker run -p 8080:8080 floodlens-kenya
```

## Cloud deployment: **not executed live**
Steps for a real deployment (documented only, no cloud credentials used this week):
1. Push the image to a container registry (e.g. Azure Container Registry).
2. Run it on a managed container service (e.g. Azure Container Apps) with HTTPS ingress only.
3. Put `OPENAI_API_KEY` and `FLOODLENS_API_KEYS` in a secret store (Key Vault / KMS), referenced by the names in
   `secret_refs.yaml`. Never in the image or the repo.
4. Set `FLOODLENS_MODE=live` only after the eval gate passes on the live model.
5. Replace the in-memory store with a database (reports, alerts, audit log of approvals).
6. Keep data in-region and document the processing under the Kenya Data Protection Act, 2019.

## Configuration
| Variable | Default | Purpose |
|---|---|---|
| `FLOODLENS_MODE` | `stub` | `live` enables the pinned model (needs `OPENAI_API_KEY`) |
| `FLOODLENS_API_KEYS` | unset | `key:role:user,...`. Unset in stub mode = teaching keys. Unset in live mode = refuse all. |
| `OPENAI_API_KEY` | unset | Live mode only. Missing key falls back to stub with a warning. |
| `PORT` | `8080` | Port used by `run_all.py` |
