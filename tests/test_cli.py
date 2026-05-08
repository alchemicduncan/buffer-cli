import json
from click.testing import CliRunner
from buffer_cli.cli import main

def test_cli_login():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["login", "--token", "test_token"])
        assert result.exit_code == 0
        assert "Access token saved successfully!" in result.output

def test_cli_user_no_token(mocker):
    mocker.patch("buffer_cli.cli.get_access_token", return_value=None)
    runner = CliRunner()
    result = runner.invoke(main, ["user"])
    assert result.exit_code == 0
    assert "Error: Not authenticated" in result.output

def test_cli_user_success(mocker, requests_mock):
    mocker.patch("buffer_cli.cli.get_access_token", return_value="fake_token")
    mock_data = {"account": {"email": "test@example.com", "id": "123"}}
    requests_mock.post("https://api.buffer.com", json={"data": mock_data})
    
    runner = CliRunner()
    result = runner.invoke(main, ["user"])
    assert result.exit_code == 0
    assert "Email: test@example.com" in result.output
    assert "ID: 123" in result.output

def test_cli_profiles_success(mocker, requests_mock):
    mocker.patch("buffer_cli.cli.get_access_token", return_value="fake_token")
    mock_data = {"account": {"channels": [{"service": "twitter", "name": "Test", "id": "p1"}]}}
    requests_mock.post("https://api.buffer.com", json={"data": mock_data})
    
    runner = CliRunner()
    result = runner.invoke(main, ["profiles"])
    assert result.exit_code == 0
    assert "Twitter - Test (ID: p1)" in result.output
