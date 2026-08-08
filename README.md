# Job Search Automation

A local-first job-search workspace that combines the MIT-licensed [ai-job-search](https://github.com/MadsLorentzen/ai-job-search) Claude Code workflow with OmniRoute free-model routing. OmniRoute remains an external local service; its source is not bundled here.

> Status: Integrated workflow. The upstream Claude Code commands and portal skills are included; application submission remains manual by design.

## End-to-end workflow

Start OmniRoute in one terminal:

```cmd
omniroute serve
```

From this repository, launch Claude Code through a free OmniRoute route:

```cmd
scripts\run-claude.cmd
```

The default profile is `auto-best-coding`. Other useful profiles are `auto-best-fast` for scraping/ranking and `auto-best-free` for a broad free fallback pool:

```cmd
scripts\run-claude-fast.cmd
scripts\run-claude-free.cmd
```

All three wrappers accept normal Claude Code arguments, for example `-p "..."`.

Inside Claude Code, run:

```text
/setup
/scrape
/rank
/apply <job-url>
/interview
/outcome
/html-report
```

Use `/setup` first. It populates the candidate profile and search preferences. `/scrape` finds jobs through the included portal skills, `/rank` creates a shortlist, and `/apply` creates the tailored CV and cover letter. Review everything and submit applications yourself.

## Which model does what?

Claude Code workflow routing uses OmniRoute's tested dynamic profiles:

| Workflow | Profile | Routing behavior |
|---|---|---|
| `/scrape`, `/rank` | `auto-best-fast` | prioritizes responsive free backends |
| `/apply`, `/interview` | `auto-best-coding` | prioritizes capable tool/reasoning backends |
| emergency fallback | `auto-best-free` | broad free-model pool |

The Python CLI in `src/` keeps an explicit fallback mapping for non-Claude-Code requests. The Claude Code profiles are generated under `~/.claude/profiles/` by OmniRoute and are separate from the repository.

## What this project does

- Sends Anthropic Messages API-compatible requests to a local OmniRoute instance.
- Selects a model profile by task (`fast`, `quality`, or `fallback`).
- Retries transient failures and tries configured fallback models.
- Stores prompts, responses, and task summaries locally as JSONL/Markdown.
- Keeps the project state independent from any one model or Claude Code profile.
- Includes the full Claude Code command and portal-skill workflow from the upstream project.
- Provides an additional Python CLI for direct ranking/chat and routing tests.

## Architecture

```text
Claude Code CLI
        |
        v
.claude commands + .agents portal skills
        |
        v
OmniRoute (external local service, http://localhost:20128)
        |
        +--> auto-best-fast
        +--> auto-best-coding
        +--> auto-best-free fallback

Direct Python CLI
        |
        v
Explicit model router + local memory + validators
        |
        v
OmniRoute Anthropic-compatible API
```

OmniRoute remains outside this repository. Install and run it separately, then configure this project to use its local endpoint. This keeps the project small and lets OmniRoute evolve independently.

## Requirements

- Python 3.10+
- Node.js and Claude Code CLI
- Bun (used by the included portal search tools)
- OmniRoute running locally
- LaTeX (`lualatex` and `xelatex`) for `/apply`
- Optional: `pdftotext` for ATS checks

The original project is designed for Claude Code. OmniRoute supplies the model endpoint; it does not replace Claude Code's local command/skill runtime.

## Quick start

### 1. Start OmniRoute

```powershell
npm install -g omniroute
omniroute serve
```

If the setup wizard asks for an Anthropic key, cancel it. The repository's tested `auto-best-*` routes use the available free backends. The gateway normally listens on `http://localhost:20128`.

### 2. Create a Python environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Set `OMNIROUTE_API_KEY` in `.env` if your OmniRoute instance requires a key. The default local development setup may accept a blank key, depending on OmniRoute configuration.

### 3. Configure Claude Code profiles

Generate the local Claude Code profiles from OmniRoute:

```cmd
omniroute setup-claude --only auto
```

The repository launcher uses `auto-best-coding` by default and routes Claude Code through OmniRoute.

### 4. Configure model profiles for the direct Python CLI

The default profiles use the free models currently exposed by OmniRoute:

| Profile | Model | Used for | Fallback order |
|---|---|---|---|
| `fast` | `oc/mimo-v2.5-free` | extraction, deduplication, scraping | quality → fallback |
| `quality` | `oc/deepseek-v4-flash-free` | ranking, CV/letter drafts, review | fallback → fast |
| `fallback` | `oc/nemotron-3-ultra-free` | recovery when the primary route fails | fast |

These model IDs are verified through the local OmniRoute `/v1/models` endpoint. Providers can change availability, so replace them with current IDs from the dashboard if necessary.

### 5. Check connectivity

```powershell
free-job-search health
```

The health command checks OmniRoute's unauthenticated `/api/init` readiness endpoint; OmniRoute's `/health` endpoint may require management authentication.

### 6. Rank a job description

```powershell
free-job-search rank --job examples/job-description.txt
```

The result is saved under `data/runs/`, and the request/response is recorded in `data/conversations/`.

### 7. Run a persistent local chat task

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

This project is an integration/orchestration layer and a prepared workspace built from the upstream workflow. It includes adapted/upstream files under `.claude`, `.agents`, `cv`, `cover_letters`, `documents`, `job_scraper`, and related folders. It does not bundle OmniRoute; OmniRoute remains a separate local service.

- [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) for the original workflow and portal/document conventions.
- [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) as an external local AI gateway.

Both upstream projects are MIT-licensed. The upstream notice is preserved in `LICENSE.ai-job-search`; preserve it when redistributing the included workflow files.

## Development

```powershell
python -m pytest
python -m compileall src
```

## Remaining work

1. Install local prerequisites (Bun and LaTeX) if they are not already installed.
2. Run `/setup` and populate the private candidate/application files.
3. Add local portal search queries and test `/scrape`.
4. Add scheduled scraping only after manual runs are reliable.
5. Add model evaluation fixtures and latency reporting.
