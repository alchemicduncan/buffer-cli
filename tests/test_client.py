import pytest
from buffer_cli.client import BufferClient

def test_buffer_client_get_user(requests_mock):
    mock_response = {"data": {"account": {"email": "test@example.com", "id": "123"}}}
    requests_mock.post("https://api.buffer.com", json=mock_response, request_headers={"Authorization": "Bearer fake_token"})
    
    client = BufferClient("fake_token")
    user_data = client.get_user()
    
    assert user_data == mock_response["data"]

def test_buffer_client_get_profiles(requests_mock):
    mock_response = {"data": {"account": {"channels": [{"service": "twitter", "name": "Test", "id": "p1"}]}}}
    requests_mock.post("https://api.buffer.com", json=mock_response, request_headers={"Authorization": "Bearer fake_token"})
    
    client = BufferClient("fake_token")
    profiles_data = client.get_profiles()
    
    assert profiles_data == mock_response["data"]
