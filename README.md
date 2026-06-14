# LoopIn

**Your AI senior friend — always in the loop, so you do not have to be.**

LoopIn is an AI-powered opportunity intelligence agent for students. It helps
students who do not have strong senior networks discover relevant hackathons,
internships, developer tools, learning resources, framework updates, and
communities before deadlines pass.

The problem is not lack of information. The problem is lack of a personalized,
trusted filter. LoopIn takes a student profile, searches and ranks signals, and
returns 5-7 conversational cards with source links and clear next actions.

## What It Does

- Collects student profile: year, tech stack, goals, interests, and location
- Runs a visible five-step reasoning pipeline
- Searches and curates hackathons, tools, learning resources, and communities
- Scores each signal by relevance, urgency, actionability, and source quality
- Writes recommendations in a friendly senior-peer tone
- Shows source-linked cards with deep-dive next steps
- Keeps safety notes and verification reminders visible

## Reasoning Pipeline

| Step | Stage | Agent Action |
| --- | --- | --- |
| 1 | Profile Intake | Structure year, stack, goals, interests, and location |
| 2 | Contextual Search | Find live opportunities, tools, news, learning, and communities |
| 3 | Relevance Reasoning | Score by urgency, alignment, and actionability |
| 4 | Personalized Synthesis | Write senior-friend cards, not generic headlines |
| 5 | Action Delivery | Attach sources, proof, and a clear next move |

## Microsoft Integration Path

The app runs immediately in frontend-only demo mode with curated, source-linked
sample data. If you run the backend and set `VITE_LOOPIN_API_URL`, it performs
real live search locally. For the preferred hackathon architecture,
[`backend/`](backend/README.md) also provides a server-side Microsoft Agent
Framework workflow using:

- Microsoft Agent Framework
- Microsoft Foundry via `FoundryChatClient`
- Foundry IQ knowledge-base retrieval for the LoopIn ranking rubric
- Microsoft Learn MCP for first-party Microsoft learning and AI-agent content
- Server-side Azure authentication through `DefaultAzureCredential`

No Azure credentials are exposed to the browser.

## Run Locally

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

Production build:

```bash
npm run check
```

## Optional Live Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
az login

export FOUNDRY_PROJECT_ENDPOINT="https://RESOURCE.ai.azure.com/api/projects/PROJECT"
export FOUNDRY_MODEL="YOUR_MODEL_DEPLOYMENT"
export FOUNDRY_IQ_MCP_URL="YOUR_FOUNDRY_IQ_KNOWLEDGE_BASE_MCP_ENDPOINT"

uvicorn app:app --app-dir backend --reload --port 8000
```

Then set this in a local `.env`:

```text
VITE_LOOPIN_API_URL=http://127.0.0.1:8000/api/plan
```

Without Foundry variables, the backend uses live web search plus trusted source
retrieval and labels the result as `Live search + trusted source retrieval`.
With Foundry IQ configured, it uses the Microsoft Foundry path.

## Reliability and Safety

- Every recommendation includes a source URL.
- Deadline-sensitive claims tell the student to verify official pages.
- The demo stores no accounts, history, or sensitive profile data.
- Backend credentials stay server-side.
- Unsupported or uncertain claims should be rejected by the Verifier Agent.

## Repository Guide

```text
backend/                 Optional live Foundry workflow
docs/architecture.svg    Architecture diagram
docs/DEMO_SCRIPT.md      Five-minute demo script
docs/SUBMISSION.md       Paste-ready submission copy
src/data/opportunities.js Curated demo opportunity signals
src/lib/agent.js         Five-step reasoning pipeline
src/App.jsx              React student-facing app
```

## Hackathon Alignment

- **Reasoning Agents:** visible multi-step search, filter, rank, synthesize, verify flow
- **Best Use of IQ Tools:** Foundry IQ integration path for grounded ranking rubric
- **Hack for Good:** reduces opportunity inequality for students without strong networks
- **User Experience:** friendly cards and deep-dive next actions
- **Reliability:** source-linked outputs and verification reminders

## Submission Materials

- [Architecture diagram](docs/architecture.svg)
- [Five-minute demo script](docs/DEMO_SCRIPT.md)
- [Paste-ready project description](docs/SUBMISSION.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md)

## License

MIT
# Loopln
