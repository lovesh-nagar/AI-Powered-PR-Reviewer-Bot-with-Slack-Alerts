"""
AI-Powered PR Reviewer Bot
--------------------------------
Triggers on Pull Requests, fetches the diff, sends it to an LLM,
posts a review comment on the PR, and alerts Slack if severity is high/critical.

Works with:
- OpenAI API (default)
- Any OpenAI-compatible endpoint (Ollama, LocalAI, Azure OpenAI, AWS Bedrock, etc.)
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


def get_env(name, default=None, required=True):
    val = os.getenv(name, default)
    if required and val is None:
        print(f"[FATAL] Missing required environment variable: {name}")
        sys.exit(1)
    return val


def fetch_pr_diff(repo, pr_number, token):
    """Fetch the unified diff of a PR from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.diff",
        "User-Agent": "ai-pr-reviewer-bot",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"[ERROR] Failed to fetch PR diff: {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.text


def call_llm(diff, api_key, base_url, model):
    """Send diff to LLM and get a structured review."""
    diff_chunk = diff[:12000]
    if len(diff) > 12000:
        diff_chunk += "\n\n... [diff truncated to fit context window] ..."

    prompt = f"""You are a senior Staff DevOps Engineer performing a code review.
Review the following Pull Request diff.

Provide your answer in this exact format:
### Summary
(2-3 sentences on what changed)

### Issues Found
- Issue: <description>
  File: <file path>
  Severity: <Low | Medium | High | Critical>
  Suggestion: <how to fix>

### Recommendations
- <bullet points for improvements>

If there are no issues, say "No major issues found."

Diff:
{diff_chunk}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    url = f"{base_url.rstrip('/')}/chat/completions"
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        print(f"[ERROR] LLM API failed: {resp.status_code} {resp.text}")
        sys.exit(1)

    return resp.json()["choices"][0]["message"]["content"]


def post_github_review(repo, pr_number, review_body, token):
    """Post the AI review as a comment on the PR."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-pr-reviewer-bot",
    }
    data = {
        "body": f"## 🤖 AI PR Reviewer Bot\n\n{review_body}",
        "event": "COMMENT",
    }
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code in (200, 201):
        print("[SUCCESS] Review posted to GitHub PR")
    else:
        print(f"[WARNING] Could not post review: {resp.status_code} {resp.text}")


def send_slack_alert(webhook_url, repo, pr_number, review_body):
    """Send Slack alert if the review contains Critical/High severity keywords."""
    if not webhook_url:
        return

    lower = review_body.lower()
    if any(k in lower for k in ["critical", "high severity", "security", "severe"]):
        message = {
            "text": f"🚨 *AI PR Review Alert*\n"
                    f"• Repository: `{repo}`\n"
                    f"• PR: #{pr_number}\n"
                    f"• Review summary:\n```{review_body[:800]}```"
        }
        try:
            requests.post(webhook_url, json=message, timeout=30)
            print("[SUCCESS] Slack alert sent")
        except requests.RequestException as e:
            print(f"[WARNING] Slack alert failed: {e}")


def main():
    # --- Env ---
    token = get_env("GITHUB_TOKEN")
    repo = get_env("GITHUB_REPOSITORY")
    llm_key = get_env("LLM_API_KEY")
    llm_base = get_env("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model = get_env("LLM_MODEL", "gpt-3.5-turbo")
    slack_webhook = get_env("SLACK_WEBHOOK_URL", "", required=False)

    # --- PR Number (from GitHub Actions env or .env for local) ---
    pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            with open(event_path) as f:
                event = json.load(f)
            pr_number = event.get("pull_request", {}).get("number")
    if not pr_number:
        print("[FATAL] Could not determine PR number")
        sys.exit(1)

    print(f"[INFO] Reviewing PR #{pr_number} in {repo}")

    # --- Pipeline ---
    diff = fetch_pr_diff(repo, pr_number, token)
    if not diff.strip():
        print("[INFO] Empty diff, skipping review.")
        return

    review = call_llm(diff, llm_key, llm_base, llm_model)
    post_github_review(repo, pr_number, review, token)
    send_slack_alert(slack_webhook, repo, pr_number, review)

    print("[INFO] Bot finished.")


if __name__ == "__main__":
    main()