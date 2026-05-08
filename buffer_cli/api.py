import requests

class BufferClient:
    BASE_URL = "https://api.bufferapp.com/1"

    def __init__(self, access_token):
        self.access_token = access_token

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.BASE_URL}/{endpoint}.json"
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        response = requests.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def get_user(self):
        return self._request("GET", "user")

    def get_profiles(self):
        return self._request("GET", "profiles")
