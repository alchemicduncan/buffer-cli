import requests

class BufferClient:
    BASE_URL = "https://api.bufferapp.com/1"

    def __init__(self, access_token):
        self.access_token = access_token

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.BASE_URL}/{endpoint}.json"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.request(method, url, params=params, data=data, headers=headers)
        if not response.ok:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except:
                error_msg = response.text
            raise requests.exceptions.HTTPError(f"{response.status_code} Client Error: {error_msg} for url: {url}", response=response)
        return response.json()

    def get_user(self):
        return self._request("GET", "user")

    def get_profiles(self):
        return self._request("GET", "profiles")
