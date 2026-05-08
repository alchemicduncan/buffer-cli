import requests

class BufferClient:
    BASE_URL = "https://api.buffer.com"

    def __init__(self, access_token):
        self.access_token = access_token

    def query(self, query_string, variables=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {"query": query_string}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.BASE_URL, json=payload, headers=headers)
        if not response.ok:
            try:
                error_data = response.json()
                # GraphQL often returns errors in an 'errors' list
                if "errors" in error_data:
                    error_msg = error_data["errors"][0].get("message", response.text)
                else:
                    error_msg = error_data.get("message", response.text)
            except:
                error_msg = response.text
            raise requests.exceptions.HTTPError(f"{response.status_code} Client Error: {error_msg} for url: {self.BASE_URL}", response=response)
        
        data = response.json()
        if "errors" in data:
            raise requests.exceptions.HTTPError(f"GraphQL Error: {data['errors'][0].get('message')}", response=response)
            
        return data.get("data")

    def get_user(self):
        query = """
        query {
          account {
            email
            id
          }
        }
        """
        return self.query(query)

    def get_profiles(self):
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
