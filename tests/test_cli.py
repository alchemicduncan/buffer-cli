from click.testing import CliRunner
from buffer_cli.cli import main


def test_cli_user_success(requests_mock):
    mock_data = {"user": {"name": "Test User", "email": "test@example.com", "id": "123"}}
    requests_mock.post("https://api.buffer.com", json={"data": mock_data})

    runner = CliRunner()
    result = runner.invoke(main, ["--token", "fake_token", "user"])
    assert result.exit_code == 0
    assert "Name: Test User" in result.output
    assert "Email: test@example.com" in result.output
    assert "ID: 123" in result.output


def test_cli_profiles_success(requests_mock):
    mock_data = {"account": {"channels": [{"service": "twitter", "name": "Test", "id": "p1"}]}}
    requests_mock.post("https://api.buffer.com", json={"data": mock_data})

    runner = CliRunner()
    result = runner.invoke(main, ["--token", "fake_token", "profiles"])
    assert result.exit_code == 0
    assert "Twitter - Test (ID: p1)" in result.output


def test_cli_token_from_env(requests_mock, monkeypatch):
    monkeypatch.setenv("BUFFER_ACCESS_TOKEN", "env_token")
    mock_data = {"user": {"name": "Env User", "email": "env@example.com", "id": "999"}}
    requests_mock.post("https://api.buffer.com", json={"data": mock_data})

    runner = CliRunner()
    result = runner.invoke(main, ["user"])
    assert result.exit_code == 0
    assert "Name: Env User" in result.output
    assert requests_mock.last_request.headers["Authorization"] == "Bearer env_token"
