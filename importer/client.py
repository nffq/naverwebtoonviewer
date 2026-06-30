import requests
from pathlib import Path
from datetime import datetime
from hmac import digest
from base64 import b64encode

class WebClient(requests.Session):
    def __init__(self, mobile_secret: bytes, mobile_agent: str, desktop_agent: str):
        super().__init__()

        self.__mobile_secret = mobile_secret
        self.__mobile_agent = mobile_agent
        self.__desktop_agent = desktop_agent

    def __fetch_mobile(self, url: str) -> dict | list:
        timestamp = int(datetime.now().timestamp() * 1000)
        signature = digest(self.__mobile_secret, f"{url}{timestamp}".encode("utf-8"), "sha256")

        response = self.get(
            url,
            headers={
                "User-Agent": self.__mobile_agent,
                "n-hmac-key-id": "AND",
                "n-hmac-signature": b64encode(signature),
                "n-hmac-timestamp": str(timestamp)
            }
        )
        response.raise_for_status()
        response = response.json()

        if response["code"] != 20002:
            raise IOError(f"invalid response: {response['message']}")

        return response["result"]

    def __fetch_desktop(self, url: str) -> requests.Response:
        response = self.get(url, headers={"User-Agent": self.__desktop_agent})
        response.raise_for_status()

        return response

    def save_media(self, url: str, path: Path):
        response = self.__fetch_desktop(url)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)

    def get_title_desktop(self, title_id: int) -> dict:
        return self.__fetch_desktop(
            f"https://comic.naver.com/api/article/list/info?titleId={title_id}"
        ).json()

    def get_title_mobile(self, title_id: int) -> dict:
        return self.__fetch_mobile(
            f"https://gateway.comic.naver.com/webtoonTitleInfo?titleId={title_id}&deviceCode=MOBILE_APP_ANDROID"
        )

    def get_author_comment(self, title_id: int, subtitle_id: int) -> dict:
        return self.__fetch_mobile(
            f"https://gateway.comic.naver.com/authorActivity?titleId={title_id}&no={subtitle_id}&deviceCode=MOBILE_APP_ANDROID"
        )

    def get_subtitle_list(self, title_id: int) -> list:
        return self.__fetch_mobile(
            f"https://gateway.comic.naver.com/webtoonArticleList?titleId={title_id}&deviceCode=MOBILE_APP_ANDROID"
        )