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
