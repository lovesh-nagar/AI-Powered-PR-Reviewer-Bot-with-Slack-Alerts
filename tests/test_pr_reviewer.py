from unittest.mock import Mock

import pytest

from src import pr_reviewer


def test_get_env_returns_existing_value(monkeypatch):
    monkeypatch.setenv("TEST_VALUE", "hello")
    assert pr_reviewer.get_env("TEST_VALUE") == "hello"


def test_get_env_returns_default(monkeypatch):
    monkeypatch.delenv("TEST_VALUE", raising=False)
    assert pr_reviewer.get_env("TEST_VALUE", "default") == "default"


def test_get_env_missing_required_exits(monkeypatch):
    monkeypatch.delenv("TEST_VALUE", raising=False)

    with pytest.raises(SystemExit):
        pr_reviewer.get_env("TEST_VALUE")


def test_fetch_pr_diff_success(monkeypatch):
    response = Mock(status_code=200, text="sample diff")
    monkeypatch.setattr(pr_reviewer.requests, "get", Mock(return_value=response))

    result = pr_reviewer.fetch_pr_diff("owner/repo", "12", "test-token")

    assert result == "sample diff"


def test_fetch_pr_diff_failure(monkeypatch):
    response = Mock(status_code=404, text="Not Found")
    monkeypatch.setattr(pr_reviewer.requests, "get", Mock(return_value=response))

    with pytest.raises(SystemExit):
        pr_reviewer.fetch_pr_diff("owner/repo", "12", "test-token")


def test_call_llm_success(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "choices": [{"message": {"content": "### Summary\nTest review"}}]
    }

    mock_post = Mock(return_value=response)
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    result = pr_reviewer.call_llm(
        diff="sample diff",
        api_key="ollama",
        base_url="http://localhost:11434/v1",
        model="qwen2.5-coder:1.5b",
    )

    assert "Test review" in result
    mock_post.assert_called_once()

    request_url = mock_post.call_args.args[0]
    assert request_url == "http://localhost:11434/v1/chat/completions"


def test_call_llm_failure(monkeypatch):
    response = Mock(status_code=500, text="Model error")
    monkeypatch.setattr(pr_reviewer.requests, "post", Mock(return_value=response))

    with pytest.raises(SystemExit):
        pr_reviewer.call_llm(
            "sample diff", "ollama",
            "http://localhost:11434/v1",
            "qwen2.5-coder:1.5b",
        )


def test_post_github_review_success(monkeypatch, capsys):
    response = Mock(status_code=201)
    mock_post = Mock(return_value=response)
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    pr_reviewer.post_github_review("owner/repo", "12", "Review text", "token")

    mock_post.assert_called_once()
    assert "[SUCCESS]" in capsys.readouterr().out


def test_post_github_review_failure(monkeypatch, capsys):
    response = Mock(status_code=403, text="Forbidden")
    monkeypatch.setattr(pr_reviewer.requests, "post", Mock(return_value=response))

    pr_reviewer.post_github_review("owner/repo", "12", "Review text", "token")

    assert "[WARNING]" in capsys.readouterr().out


def test_slack_alert_skips_without_webhook(monkeypatch):
    mock_post = Mock()
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    pr_reviewer.send_slack_alert("", "owner/repo", "12", "Critical security issue")

    mock_post.assert_not_called()


def test_slack_alert_sends_for_security_issue(monkeypatch):
    mock_post = Mock()
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    pr_reviewer.send_slack_alert(
        "https://example.com/webhook",
        "owner/repo",
        "12",
        "Critical security issue found",
    )

    mock_post.assert_called_once()


def test_slack_alert_skips_low_severity_review(monkeypatch):
    mock_post = Mock()
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    pr_reviewer.send_slack_alert(
        "https://example.com/webhook",
        "owner/repo",
        "12",
        "Minor formatting suggestion",
    )

    mock_post.assert_not_called()


def test_slack_alert_handles_request_exception(monkeypatch, capsys):
    mock_post = Mock(side_effect=pr_reviewer.requests.RequestException("Network unavailable"))
    monkeypatch.setattr(pr_reviewer.requests, "post", mock_post)

    pr_reviewer.send_slack_alert(
        "https://example.com/webhook",
        "owner/repo",
        "12",
        "High severity issue",
    )

    assert "[WARNING]" in capsys.readouterr().out
