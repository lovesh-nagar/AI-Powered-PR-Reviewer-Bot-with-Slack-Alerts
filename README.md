<<<<<<< HEAD
# 🤖 AI-Powered PR Reviewer Bot with Slack Alerts

A complete DevOps project that automatically reviews Pull Requests using an LLM and sends Slack alerts for Critical/High severity findings.

## 🎯 What it does

1. Triggers on every Pull Request (`opened`, `synchronize`, `reopened`)
2. Fetches the PR diff from GitHub
3. Sends the diff to an LLM (OpenAI or any OpenAI-compatible endpoint)
4. Posts a structured AI review comment on the PR
5. Sends a Slack alert if Critical/High severity issues are detected

## 📁 Project Structure

```text
ai-pr-reviewer-bot/
├── .github/
│   └── workflows/
│       └── ai-pr-reviewer.yml    # GitHub Action workflow
├── src/
│   └── pr_reviewer.py            # Main bot logic (Python)
├── requirements.txt              # Python dependencies
├── .env.example                  # Example environment variables
├── Dockerfile                    # Optional: containerized run
├── .gitignore                    # Ignore secrets and cache
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone this repository
```bash
git clone https://github.com/lovesh-nagar/AI-Powered-PR-Reviewer-Bot-with-Slack-Alerts.git
cd AI-Powered-PR-Reviewer-Bot-with-Slack-Alerts
```

### 2. Get your secrets

| Secret | Where to get it |
|--------|-----------------|
| `LLM_API_KEY` | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| `LLM_BASE_URL` | Default: `https://api.openai.com/v1`. For Ollama: `http://localhost:11434/v1` |
| `LLM_MODEL` | `gpt-3.5-turbo`, `gpt-4o`, or `llama3` (Ollama) |
| `SLACK_WEBHOOK_URL` | Slack → Apps → Incoming Webhooks |

> 💡 **Free option:** Install [Ollama](https://ollama.com), run `ollama pull llama3`, then use `LLM_BASE_URL=http://localhost:11434/v1` and `LLM_MODEL=llama3` with no API key needed.

### 3. Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Add these four secrets:

| Name | Value |
|------|-------|
| `LLM_API_KEY` | your key (or `dummy` if using Ollama) |
| `LLM_BASE_URL` | `https://api.openai.com/v1` |
| `LLM_MODEL` | `gpt-3.5-turbo` |
| `SLACK_WEBHOOK_URL` | your Slack webhook URL |

`GITHUB_TOKEN` is provided automatically by GitHub Actions.

### 4. Test it

1. Create a new branch and make a code change.
2. Open a Pull Request.
3. Watch the **Actions** tab — the `ai-review` job will run.
4. Check the PR — an AI review comment will appear.
5. If the AI finds Critical/High issues, a Slack message hits your channel.

## 🛠 Local Testing

```bash
# Copy env template
cp .env.example .env
# Edit .env with your values (PR_NUMBER=1, etc.)

# Install dependencies
pip install -r requirements.txt

# Run against a real PR number
export PR_NUMBER=1
python src/pr_reviewer.py
```

## 🐳 Docker (optional)

```bash
docker build -t ai-pr-reviewer .
docker run --env-file .env ai-pr-reviewer
```

## 📊 Resume / Profile

Add this to your resume under **Projects**:

> *AI-Powered PR Reviewer Bot — Automated code review using LLMs in GitHub Actions. Slack integration for critical severity alerts. Stack: Python, GitHub Actions, OpenAI API, Slack Webhooks, Docker.*

## 🔐 Security

- Never commit real API keys or tokens.
- All secrets are injected via GitHub Actions Secrets.
- The bot only **comments** on PRs — it does not merge or push code.

## 🛣 Roadmap

- [ ] Inline review comments (per-file line annotations)
- [ ] Auto-labeling (`ai-approved`, `needs-review`)
- [ ] Multi-LLM support (Anthropic, AWS Bedrock, Azure OpenAI)
- [ ] Review history dashboard

---

Built as part of an AI + DevOps learning path.
=======
# AI-Powered-PR-Reviewer-Bot-with-Slack-Alerts
>>>>>>> 43eb52d53dd8515a9af97e0a942bdcdb32c2d647
