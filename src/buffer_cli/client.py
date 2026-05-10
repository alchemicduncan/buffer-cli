from __future__ import annotations

import httpx

ACCESS_TOKEN_ENV = "BUFFER_ACCESS_TOKEN"


class BufferError(Exception):
    """Raised when a Buffer API request fails (HTTP error or GraphQL error)."""


class BufferClient:
    BASE_URL = "https://api.buffer.com"

    def __init__(self, access_token):
        self.access_token = access_token
        self._http = httpx.Client()

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.close()

    def query(self, query_string, variables=None, use_bearer=True):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            if use_bearer:
                headers["Authorization"] = f"Bearer {self.access_token}"
            else:
                headers["Authorization"] = self.access_token

        payload = {"query": query_string}
        if variables:
            payload["variables"] = variables

        response = self._http.post(self.BASE_URL, json=payload, headers=headers)

        if response.status_code == 401 and use_bearer:
            return self.query(query_string, variables, use_bearer=False)

        if response.is_error:
            try:
                error_data = response.json()
                if "errors" in error_data:
                    error_msg = error_data["errors"][0].get("message", response.text)
                else:
                    error_msg = error_data.get("message", response.text)
            except ValueError:
                error_msg = response.text
            raise BufferError(f"{response.status_code} Client Error: {error_msg} for url: {self.BASE_URL}")

        data = response.json()
        if "errors" in data:
            raise BufferError(f"GraphQL Error: {data['errors'][0].get('message')}")

        return data.get("data")

    def get_user(self):
        query = """
        query {
          account {
            id
            email
            name
          }
        }
        """
        return self.query(query)

    def get_channels(self):
        query = """
        query {
          account {
            channels {
              id
              name
              service
            }
          }
        }
        """
        return self.query(query)
