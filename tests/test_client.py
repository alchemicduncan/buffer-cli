import httpx
import respx

from buffer_cli.client import BufferClient, BufferError


@respx.mock
def test_buffer_client_get_user():
    mock_response = {"data": {"account": {"id": "123", "email": "test@example.com", "name": "Test"}}}
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    client = BufferClient("fake_token")
    user_data = client.get_user()

    assert user_data == mock_response["data"]
    assert route.calls.last.request.headers["Authorization"] == "Bearer fake_token"


@respx.mock
def test_buffer_client_get_channels():
    mock_response = {"data": {"account": {"channels": [{"service": "twitter", "name": "Test", "id": "p1"}]}}}
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    client = BufferClient("fake_token")
    channels_data = client.get_channels()

    assert channels_data == mock_response["data"]


@respx.mock
def test_buffer_client_retries_without_bearer_on_401():
    route = respx.post("https://api.buffer.com").mock(
        side_effect=[
            httpx.Response(401, json={"message": "unauthorized"}),
            httpx.Response(200, json={"data": {"account": {"id": "1"}}}),
        ]
    )
    client = BufferClient("oidc_token")
    data = client.get_user()
    assert data == {"account": {"id": "1"}}
    assert route.call_count == 2
    assert route.calls[0].request.headers["Authorization"] == "Bearer oidc_token"
    assert route.calls[1].request.headers["Authorization"] == "oidc_token"


@respx.mock
def test_buffer_client_raises_on_http_error():
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(500, json={"message": "boom"})
    )
    client = BufferClient("fake_token")
    try:
        client.get_user()
    except BufferError as exc:
        assert "boom" in str(exc)
        return
    raise AssertionError("Expected BufferError")


@respx.mock
def test_buffer_client_create_post_success():
    post_payload = {
        "id": "post_1",
        "status": "draft",
        "text": "hello world",
        "createdAt": "2026-05-09T00:00:00Z",
        "dueAt": None,
        "channelId": "ch_1",
        "channelService": "bluesky",
        "shareMode": "addToQueue",
    }
    route = respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={
            "data": {"createPost": {"__typename": "PostActionSuccess", "post": post_payload}}
        })
    )

    client = BufferClient("fake_token")
    result = client.create_post(channel_id="ch_1", text="hello world", save_to_draft=True)

    assert result == post_payload
    sent = route.calls.last.request
    assert b'"channelId":"ch_1"' in sent.content
    assert b'"saveToDraft":true' in sent.content


@respx.mock
def test_buffer_client_create_post_raises_on_error_union():
    respx.post("https://api.buffer.com").mock(
        return_value=httpx.Response(200, json={
            "data": {"createPost": {"__typename": "InvalidInputError", "message": "bad text"}}
        })
    )

    client = BufferClient("fake_token")
    try:
        client.create_post(channel_id="ch_1", text="")
    except BufferError as exc:
        assert "InvalidInputError" in str(exc)
        assert "bad text" in str(exc)
        return
    raise AssertionError("Expected BufferError on InvalidInputError union member")
