import json

import httpx
import respx
from click.testing import CliRunner

from buffer_cli.cli import main


@respx.mock
def test_cli_user_success():
    mock_data = {"account": {"id": "123", "email": "test@example.com", "name": "Test User"}}
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={"data": mock_data})
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--token", "fake_token", "user"])
    assert result.exit_code == 0
    assert json.loads(result.output) == mock_data


@respx.mock
def test_cli_channels_list_success():
    mock_data = {"account": {"channels": [{"service": "twitter", "name": "Test", "id": "p1"}]}}
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={"data": mock_data})
    )

    runner = CliRunner()
    result = runner.invoke(main, ["--token", "fake_token", "channels", "list"])
    assert result.exit_code == 0
    assert json.loads(result.output) == mock_data


@respx.mock
def test_cli_token_from_env(monkeypatch):
    monkeypatch.setenv("BUFFER_ACCESS_TOKEN", "env_token")
    mock_data = {"account": {"id": "999", "email": "env@example.com", "name": "Env User"}}
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={"data": mock_data})
    )

    runner = CliRunner()
    result = runner.invoke(main, ["user"])
    assert result.exit_code == 0
    assert json.loads(result.output) == mock_data
    assert route.calls.last.request.headers["Authorization"] == "Bearer env_token"


@respx.mock
def test_cli_exits_nonzero_on_api_error():
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(500, json={"message": "boom"})
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--token", "fake_token", "user"])
    assert result.exit_code == 1


def _create_post_mock_response(post=None):
    return {
        "data": {
            "createPost": {
                "__typename": "PostActionSuccess",
                "post": post or {"id": "p_1", "status": "draft", "text": "hi"},
            }
        }
    }


@respx.mock
def test_cli_posts_create_default_is_draft():
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json=_create_post_mock_response())
    )

    runner = CliRunner()
    result = runner.invoke(main, [
        "--token", "fake_token", "posts", "create",
        "--channel", "ch_1", "--text", "hello",
    ])
    assert result.exit_code == 0, result.output
    body = route.calls.last.request.content
    assert b'"saveToDraft":true' in body
    assert b'"mode":"addToQueue"' in body
    assert b'"schedulingType":"automatic"' in body


@respx.mock
def test_cli_posts_create_share_now():
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json=_create_post_mock_response())
    )

    runner = CliRunner()
    result = runner.invoke(main, [
        "--token", "fake_token", "posts", "create",
        "--channel", "ch_1", "--text", "hi", "--share-now",
    ])
    assert result.exit_code == 0, result.output
    body = route.calls.last.request.content
    assert b'"saveToDraft":false' in body
    assert b'"mode":"shareNow"' in body


@respx.mock
def test_cli_posts_create_at_uses_custom_scheduled():
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json=_create_post_mock_response())
    )

    runner = CliRunner()
    result = runner.invoke(main, [
        "--token", "fake_token", "posts", "create",
        "--channel", "ch_1", "--text", "hi", "--at", "2026-06-01T14:00:00Z",
    ])
    assert result.exit_code == 0, result.output
    body = route.calls.last.request.content
    assert b'"mode":"customScheduled"' in body
    assert b'"dueAt":"2026-06-01T14:00:00Z"' in body


def test_cli_posts_create_mode_flags_are_mutually_exclusive():
    runner = CliRunner()
    result = runner.invoke(main, [
        "--token", "fake_token", "posts", "create",
        "--channel", "ch_1", "--text", "hi", "--share-now", "--add-to-queue",
    ])
    assert result.exit_code == 2
    assert "mutually" in result.output or "at most one" in result.output


@respx.mock
def test_cli_posts_create_surfaces_union_error():
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={
            "data": {"createPost": {"__typename": "InvalidInputError", "message": "text required"}}
        })
    )
    runner = CliRunner()
    result = runner.invoke(main, [
        "--token", "fake_token", "posts", "create",
        "--channel", "ch_1", "--text", "",
    ])
    assert result.exit_code == 1
