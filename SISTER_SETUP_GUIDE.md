# Job Search Automation — Clean Computer Setup

This guide is for a new computer where the user has Codex but no development tools.

The normal setup uses two terminals:

```text
Terminal 1: OmniRoute local AI gateway
                 |
                 v
Terminal 2: Claude Code + this job-search-automation repository
```

There is only one OmniRoute server. The job-search project is not a second server;
it is a Claude Code workspace that connects to OmniRoute.

## Before starting

The user needs a GitHub account, Codex, permission to install software, and a CV/resume.
Do not put API keys, passwords, passport information, or private contact data in public chat.

## 1. Clone the repository

In Codex, open a parent folder such as Documents and ask:

```text
Clone https://github.com/anurag-joshi11/job-search-automation.git into this folder.
Do not modify files yet. Confirm the repository path and show git status.
```

Or use a terminal:

```powershell
git clone https://github.com/anurag-joshi11/job-search-automation.git
cd job-search-automation
git status
```

## 2. Install all required tools

| Tool | Purpose | Check |
|---|---|---|
| Git | Clone/update the repository | `git --version` |
| Node.js LTS | Runs npm, OmniRoute, and Claude Code | `node --version` |
| npm | Installs Node tools | `npm --version` |
| Python 3.10+ | Runs the direct router and tests | `py --version` |
| Bun | Runs portal-search CLIs | `bun --version` |
| Claude Code CLI | Reads `.claude/` commands and skills | `claude --version` |
| OmniRoute CLI | Provides the local free-model endpoint | `omniroute --version` |

### Windows

Ask Codex:

```text
Check whether Git, Node.js LTS, Python 3.10+, and Bun are installed. For every
missing tool, tell me what you will install, install it from an official source,
and verify it. Do not install duplicate copies.
```

If using Windows Package Manager:

```powershell
winget install --id Git.Git -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.13 -e
winget install --id Oven-sh.Bun -e
```

Close and reopen Codex/PowerShell after installation so the updated PATH loads.

### macOS

With Homebrew:

```bash
brew install git node python
brew install oven-sh/bun/bun
```

### Linux

Ask Codex to identify the Linux distribution and provide package-manager commands
for Git, Node.js LTS, Python 3.10+, and Bun. Do not replace existing packages
without asking first.

## 3. Install Claude Code and OmniRoute

From a terminal with Node.js/npm available:

```powershell
npm install -g @anthropic-ai/claude-code
npm install -g omniroute
claude --version
omniroute --version
```

OmniRoute is installed globally outside this repository. The repository contains
the workflow and launch wrappers, not the OmniRoute server itself.

## 4. Configure OmniRoute without an Anthropic key

Run:

```powershell
omniroute setup
```

If the wizard asks for an Anthropic API key, do not invent one or enter a password.
Skip or exit that provider setup. This project uses OmniRoute's available free routes.

Generate local Claude Code profiles:

```powershell
omniroute setup-claude --only auto
```

These profiles are machine-local under `%USERPROFILE%\.claude\profiles\` on Windows
or `~/.claude/profiles/` on macOS/Linux. Do not commit them to GitHub.

## 5. Create the Python environment

Windows PowerShell:

```powershell
cd "C:\path\to\job-search-automation"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
free-job-search --help
```

macOS/Linux:

```bash
cd /path/to/job-search-automation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
free-job-search --help
```

Do not add API keys to `.env` unless a provider explicitly requires one.

## 6. Install the portal-search dependencies

Windows PowerShell:

```powershell
$tools = @("jobbank-search", "jobdanmark-search", "jobindex-search", "jobnet-search", "linkedin-search", "freehire-search")
foreach ($tool in $tools) {
  Push-Location ".agents\skills\$tool\cli"
  bun install
  Pop-Location
}
```

macOS/Linux:

```bash
for tool in jobbank-search jobdanmark-search jobindex-search jobnet-search linkedin-search freehire-search; do
  (cd ".agents/skills/$tool/cli" && bun install)
done
```

## 7. Install PDF/document tools

The `/apply` workflow creates PDF CVs and cover letters. Install:

- Windows: MiKTeX.
- macOS: MacTeX.
- Linux: TeX Live.

Verify:

```text
lualatex --version
xelatex --version
```

For the optional ATS text check, install Poppler and verify:

```text
pdftotext -version
```

Searching and ranking can work without LaTeX, but `/apply` cannot reliably create
final PDFs without it.

## 8. Start the two applications

### Terminal 1 — OmniRoute

```powershell
omniroute serve --port 20128
```

Leave this terminal open. Check it from another terminal:

```powershell
Invoke-WebRequest http://localhost:20128/api/init -UseBasicParsing
```

### Terminal 2 — job-search-automation through Claude Code

```powershell
cd "C:\path\to\job-search-automation"
scripts\run-claude.cmd
```

Optional route wrappers:

```powershell
scripts\run-claude-fast.cmd
scripts\run-claude-free.cmd
```

Accept the Claude Code workspace-trust prompt only after confirming that the opened
folder is the cloned repository. Do not start a second OmniRoute server.

## 9. Complete private onboarding

Inside Claude Code, run:

```text
/setup
```

Add a CV, add documents under the local `documents/` folder, or answer the interview
questions. The onboarding updates the canonical profile files described by `AGENTS.md`.
Do not create a second profile system.

## 10. Run the workflow

```text
/scrape
/rank
/apply <job-url>
/interview
/html-report
/outcome
```

Review every generated claim and document. Applications are submitted manually.

## 11. Ask Codex to verify the installation

From the repository root, paste:

```text
Verify this installation without modifying personal files. Check Git, Node.js,
npm, Python, Bun, Claude Code, OmniRoute, lualatex, xelatex, and pdftotext.
Check OmniRoute /api/init, run the Python health check, and compile the Python
source. Report each check as PASS, OPTIONAL, or FAIL with the exact next command.
Do not run /setup, /scrape, or /apply.
```

Minimum Windows checks:

```powershell
git --version
node --version
npm --version
py --version
bun --version
claude --version
omniroute --version
.\.venv\Scripts\free-job-search.exe health
python -m compileall src
```

## Troubleshooting

### `omniroute` or `claude` is not recognized

Close and reopen the terminal, then run:

```powershell
where.exe node
where.exe omniroute
where.exe claude
```

### OmniRoute is unavailable

Confirm Terminal 1 is still running and test:

```powershell
Invoke-WebRequest http://localhost:20128/api/init -UseBasicParsing
```

Do not start another server on the same port. Ask Codex to identify the owning
process before stopping anything.

### Claude Code asks for an Anthropic key

Do not enter a made-up key. Confirm OmniRoute is running first and Claude Code was
launched with `scripts\run-claude.cmd`.

### `/scrape` fails

Check Bun and repeat Step 6. Respect job-board terms, robots rules, rate limits,
and authentication requirements.

### `/apply` fails

Check `lualatex`, `xelatex`, the LaTeX distribution's package policy, and `pdftotext`.

## Canonical instructions and references

The canonical workflow rules remain in `AGENTS.md`, `CLAUDE.md`, `.claude/`, and
`.agents/skills/`. This document only explains clean-computer installation.

- [Codex by OpenAI](https://developers.openai.com/codex/)
- [This project](https://github.com/anurag-joshi11/job-search-automation)
- [Original ai-job-search project](https://github.com/MadsLorentzen/ai-job-search)
- [OmniRoute project](https://github.com/diegosouzapw/OmniRoute)

To stop everything, press `Ctrl+C` in Terminal 2 and then Terminal 1.
