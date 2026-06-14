# Live Microsoft Foundry workflow

The browser prototype runs without credentials. This backend enables two live
paths:

- **Foundry mode:** uses Microsoft Agent Framework, Microsoft Foundry, Foundry
  IQ, and Microsoft Learn MCP.
- **No-secret live-search fallback:** if Foundry IQ is not configured, the API
  uses live web result feeds plus trusted live source checks so the demo can
  still show real search/retrieval behavior without exposing secrets.

Foundry mode is the preferred competition architecture:

1. Microsoft Agent Framework orchestrates five specialist agents.
2. `FoundryChatClient` runs the agents through a Microsoft Foundry project.
3. The Search Agent calls Microsoft Learn MCP for Microsoft learning and
   Foundry-related signals.
4. The same workflow retrieves the LoopIn ranking rubric through a Foundry IQ knowledge
   base exposed as an MCP endpoint.
5. The Verifier returns source-linked opportunity cards rendered by the React app.

## Configuration

Use Python 3.10-3.13, then:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
az login
```

Set environment variables without committing them:

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://RESOURCE.ai.azure.com/api/projects/PROJECT"
export FOUNDRY_MODEL="YOUR_MODEL_DEPLOYMENT"
export FOUNDRY_IQ_MCP_URL="YOUR_FOUNDRY_IQ_KNOWLEDGE_BASE_MCP_ENDPOINT"
```

Start the API:

```bash
uvicorn app:app --app-dir backend --reload --port 8000
```

Set `VITE_LOOPIN_API_URL=http://127.0.0.1:8000/api/plan` in a local `.env` and
start the frontend with `npm run dev`.

The Microsoft Learn MCP server is read-only and requires no authentication.
Foundry authentication uses `DefaultAzureCredential`; no keys are placed in the
source code or browser.

If you skip the Foundry variables, `/api/plan` falls back to live search plus
trusted source retrieval and returns `mode: "Live search + trusted source
retrieval"`. Use that only as a demo fallback; do not describe it as Foundry IQ
execution.
