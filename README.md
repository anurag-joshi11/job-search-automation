# Free AI Job Search

A local-first, provider-agnostic job-search assistant that can use free-tier models through [OmniRoute](https://github.com/diegosouzapw/OmniRoute). It is designed to complement the MIT-licensed [ai-job-search](https://github.com/MadsLorentzen/ai-job-search) workflow without bundling OmniRoute or copying its source code.

> Status: MVP scaffold. The routing, fallback, memory, and validation layers are implemented. Portal-specific scraping and automatic application submission are intentionally out of scope until they can be tested safely.

## What this project does

- Sends Anthropic Messages API-compatible requests to a local OmniRoute instance.
- Selects a model profile by task (`fast`, `quality`, or `fallback`).
- Retries transient failures and tries configured fallback models.
- Stores prompts, responses, and task summaries locally as JSONL/Markdown.
- Keeps the project state independent from any one model or Claude Code profile.
- Provides a small CLI that can rank a saved job description and run a chat task.

## Architecture

```text
CLI / future Claude Code skills
        |
        v
Task router -> memory/context loader -> output validator
        |
        v
OmniRoute (external local service, http://localhost:20128)
        |
        +--> fast free model
        +--> quality free model
        +--> fallback free model
```

OmniRoute remains outside this repository. Install and run it separately, then configure this project to use its local endpoint. This keeps the project small and lets OmniRoute evolve independently.

## Requirements

- Python 3.10+
- OmniRoute running locally
- At least one provider/model configured in OmniRoute

Optional dependencies for the larger job-search workflow include Bun, LaTeX, and `pdftotext`; those will be added when portal adapters and document generation are integrated.

## Quick start

### 1. Start OmniRoute

```powershell
npm install -g omniroute
omniroute setup
omniroute
```

Configure at least one provider in the OmniRoute dashboard. The gateway normally listens on `http://localhost:20128`.

### 2. Create a Python environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Set `OMNIROUTE_API_KEY` in `.env` if your OmniRoute instance requires a key. The default local development setup may accept a blank key, depending on OmniRoute configuration.

### 3. Configure model profiles

Edit [`config/models.json`](config/models.json) and replace the example model IDs with IDs enabled in your OmniRoute dashboard. Keep the profile names stable; the router uses them by task.

### 4. Check connectivity

```powershell
free-job-search health
```

### 5. Rank a job description

```powershell
free-job-search rank --job examples/job-description.txt
```

The result is saved under `data/runs/`, and the request/response is recorded in `data/conversations/`.

### 6. Run a persistent local chat task

```powershell
free-job-search chat --task general
```

The CLI loads the local profile and rolling memory before each request. Conversation history is stored locally; it is not dependent on the model remembering previous sessions.

## Model routing and fallbacks

The router uses task profiles rather than changing models arbitrarily inside a multi-step workflow:

| Task | Default profile | Purpose |
|---|---|---|
| `scrape`, `extract`, `deduplicate` | `fast` | Short structured transformations |
| `rank`, `general` | `quality` | Reasoning over a job and candidate profile |
| `write_cv`, `write_letter`, `review` | `quality` | Highest-quality available model |
| provider failure | configured fallback chain | Recovery from quota/timeouts |

Fallbacks are for technical failures such as timeouts, 429s, and 5xx responses. They are not a guarantee that a weaker model will produce equally good writing. Every final CV or letter must be reviewed by a person.

The router does not switch models halfway through a tool-use loop. Each request is retried at a clean request boundary, and completed workflow steps are written to disk before the next step starts.

## Memory and chat history

Model context is not permanent memory. This project stores durable state locally:

```text
data/
├── conversations/       # JSONL request/response history
├── memory/              # rolling summary and long-term preferences
├── profile/             # candidate data; ignored by Git
├── jobs/                # raw and normalized postings; ignored by Git
└── runs/                # generated reports; ignored by Git
```

The important workflow state is reconstructed from these files when a new model or fallback provider is used. Do not commit personal CVs, contact information, application history, or API keys.

## Safety boundaries

- No automatic job application submission is included.
- Job descriptions are treated as untrusted content.
- Personal data directories are Git-ignored by default.
- Model output is validated for basic structure, but semantic truthfulness still requires human review.
- Job-board access rules and rate limits must be respected.

## Relationship to upstream projects

This project is an integration/orchestration layer, not a replacement claim for either upstream project. It is intended to work alongside:

- [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) for the broader job-search workflow and document conventions.
- [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) as an external local AI gateway.

Both upstream projects are MIT-licensed. Preserve their license notices when distributing copied or substantially derived code. This repository currently does not bundle their source.

## Development

```powershell
python -m pytest
python -m compileall src
```

## Roadmap

1. Add portal adapters with rate limiting and deduplication.
2. Add structured ranking schemas and deterministic profile checks.
3. Add CV/cover-letter generation with PDF/ATS validation.
4. Add Claude Code skill wrappers that call the same router.
5. Add a local dashboard and scheduled scrape command.
6. Add model evaluation fixtures so routing decisions are measurable.

