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
    mock_user = {"name": "Test User"}
    requests_mock.get("https://api.bufferapp.com/1/user.json", json=mock_user, request_headers={"Authorization": "Bearer fake_token"})
    
    runner = CliRunner()
    result = runner.invoke(main, ["user"])
    assert result.exit_code == 0
    assert json.loads(result.output) == mock_user

def test_cli_profiles_success(mocker, requests_mock):
    mocker.patch("buffer_cli.cli.get_access_token", return_value="fake_token")
    mock_profiles = [{"service": "twitter", "formatted_username": "@test", "id": "p1"}]
    requests_mock.get("https://api.bufferapp.com/1/profiles.json", json=mock_profiles, request_headers={"Authorization": "Bearer fake_token"})
    
    runner = CliRunner()
    result = runner.invoke(main, ["profiles"])
    assert result.exit_code == 0
    assert "Twitter - @test (ID: p1)" in result.output
