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

    def get_default_organization_id(self):
        data = self.query("{ account { organizations { id } } }")
        orgs = data.get("account", {}).get("organizations") or []
        if not orgs:
            raise BufferError("No organizations found on this account")
        return orgs[0]["id"]

    def list_posts(self, organization_id=None, statuses=None, channel_ids=None, first=30):
        if organization_id is None:
            organization_id = self.get_default_organization_id()

        input_dict = {"organizationId": organization_id}
        filter_dict = {}
        if statuses:
            filter_dict["status"] = list(statuses)
        if channel_ids:
            filter_dict["channelIds"] = list(channel_ids)
        if filter_dict:
            input_dict["filter"] = filter_dict

        query = """
        query ListPosts($input: PostsInput!, $first: Int) {
          posts(input: $input, first: $first) {
            edges {
              cursor
              node {
                id
                status
                text
                createdAt
                dueAt
                sentAt
                channelId
                channelService
                shareMode
                externalLink
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """
        data = self.query(query, variables={"input": input_dict, "first": first})
        result = data["posts"]
        return {
            "posts": [edge["node"] for edge in result.get("edges", [])],
            "pageInfo": result.get("pageInfo", {}),
        }

    def create_post(
        self,
        channel_id,
        text,
        mode="addToQueue",
        scheduling_type="automatic",
        save_to_draft=False,
        due_at=None,
        tag_ids=None,
    ):
        input_dict = {
            "channelId": channel_id,
            "text": text,
            "mode": mode,
            "schedulingType": scheduling_type,
            "saveToDraft": save_to_draft,
        }
        if due_at:
            input_dict["dueAt"] = due_at
        if tag_ids:
            input_dict["tagIds"] = list(tag_ids)

        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            __typename
            ... on PostActionSuccess {
              post {
                id
                status
                text
                createdAt
                dueAt
                channelId
                channelService
                shareMode
              }
            }
            ... on NotFoundError { message }
            ... on UnauthorizedError { message }
            ... on UnexpectedError { message }
            ... on RestProxyError { message link code }
            ... on LimitReachedError { message }
            ... on InvalidInputError { message }
          }
        }
        """
        data = self.query(mutation, variables={"input": input_dict})
        result = data["createPost"]
        if result.get("__typename") == "PostActionSuccess":
            return result["post"]
        message = result.get("message", "unknown error")
        raise BufferError(f"{result.get('__typename', 'UnknownError')}: {message}")
