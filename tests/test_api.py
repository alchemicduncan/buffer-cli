import pytest
from buffer_cli.api import BufferClient

def test_buffer_client_get_user(requests_mock):
    mock_response = {"name": "Test User", "id": "123"}
    requests_mock.get("https://api.bufferapp.com/1/user.json?access_token=fake_token", json=mock_response)
    
    client = BufferClient("fake_token")
    user = client.get_user()
    
    assert user == mock_response

def test_buffer_client_get_profiles(requests_mock):
    mock_response = [{"service": "twitter", "formatted_username": "@test", "id": "p1"}]
    requests_mock.get("https://api.bufferapp.com/1/profiles.json?access_token=fake_token", json=mock_response)
    
    client = BufferClient("fake_token")
    profiles = client.get_profiles()
    
    assert profiles == mock_response
