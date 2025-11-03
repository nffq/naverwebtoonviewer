import os
import requests
import sqlite3
from base64 import b64encode
from datetime import datetime
from typing import List
from tqdm import tqdm
from mimetypes import guess_extension
from cryptography.hazmat.primitives import hashes, hmac
from urllib.parse import quote

class WebtoonClient:
    def __init__(self, secret: str, mobile_agent: str, desktop_agent: str) -> None:
        self.session = requests.Session()
        self.secret = secret.encode("utf-8")
        self.mobile_agent = mobile_agent
        self.desktop_agent = desktop_agent

    def close(self) -> None:
        self.session.close()

    def __get_mobile(self, url: str) -> dict:
        timestamp = int(datetime.now().timestamp() * 1000)

        signer = hmac.HMAC(self.secret, hashes.SHA1())
        signer.update(f"{url}{timestamp}".encode("utf-8"))
        signature = quote(b64encode(signer.finalize()), safe="")

        response = self.session.get(
            f"{url}&msgpad={timestamp}&md={signature}",
            headers={"User-Agent": self.mobile_agent}
        ).json()
        if response["code"] != 20002:
            raise IOError(f"failed: {response["message"]}")
        return response["result"]

    def __get_desktop(self, url: str) -> requests.Response:
        response = self.session.get(url, headers={"User-Agent": self.desktop_agent})
        response.raise_for_status()
        return response

    def fetch_title_info_desktop(self, title_id: int) -> dict:
        return self.__get_desktop(
            f"https://comic.naver.com/api/article/list/info?titleId={title_id}"
        ).json()

    def fetch_title_info_mobile(self, title_id: int) -> dict:
        return self.__get_mobile(
            f"https://apis.naver.com/mobiletoon/comic/webtoonTitleInfo.json?titleId={title_id}&deviceCode=MOBILE_APP_ANDROID"
        )

    def fetch_subtitle_list(self, title_id: int) -> List[dict]:
        return self.__get_mobile(
            f"https://apis.naver.com/mobiletoon/comic/webtoonArticleList.json?titleId={title_id}&deviceCode=MOBILE_APP_ANDROID"
        )

    def fetch_author_comment(self, title_id: int, subtitle_id: int) -> dict:
        return self.__get_mobile(
            f"https://apis.naver.com/mobiletoon/comic/authorActivity?titleId={title_id}&no={subtitle_id}&deviceCode=MOBILE_APP_ANDROID"
        )

    def fetch_media(self, url: str, destination: str) -> str:
        response = self.__get_desktop(url)
        media_location = f"{destination}{guess_extension(response.headers["Content-Type"])}"
        os.makedirs(os.path.dirname(media_location), exist_ok=True)
        with open(media_location, "wb") as file:
            file.write(response.content)
        return media_location


def fetch_title_data(client: WebtoonClient, title_id: int) -> None:
    res = {}

    title_info_desktop = client.fetch_title_info_desktop(title_id)
    if title_info_desktop["webtoonLevelCode"] != "WEBTOON":
        raise ValueError("not a webtoon")

    title_info_mobile = client.fetch_title_info_mobile(title_id)
    subtitle_list = client.fetch_subtitle_list(title_id)

    res["title"] = {
        "id": title_info_desktop["titleId"],
        "name": title_info_desktop["titleName"],
        "synopsis": title_info_desktop["synopsis"],
        "thumbnail": client.fetch_media(title_info_desktop["thumbnailUrl"], f"media/{title_id}/thumbnail"),
        "banner": client.fetch_media(title_info_mobile["title"]["illustCardUrl"], f"media/{title_id}/banner")
    }

    res["subtitles"] = []
    for subtitle in tqdm(subtitle_list, desc="fetching subtitles"):
        date = datetime.strptime(subtitle["serviceDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
        comment = client.fetch_author_comment(title_id, subtitle["no"])
        comment = next(filter(lambda t: t["type"] == "COMMENT", comment["postList"]), {})
        thumbnail = client.fetch_media(subtitle["thumbnailUrl"], f"media/{title_id}/thumbnails/{subtitle["no"]}")

        res["subtitles"].append(
            {
                "id": subtitle["no"],
                "name": subtitle["subtitle"],
                "date": int(date.timestamp()),
                "thumbnail": thumbnail,
                "comment": comment.get("content", ".")
            }
        )

    res["artists"] = []
    role_map = {
        "ARTIST_WRITER": "글",
        "ARTIST_PAINTER": "그림",
        "ARTIST_NOVEL_ORIGIN": "원작"
    }
    for artist in title_info_desktop["communityArtists"]:
        res["artists"].append(
            {
                "id": artist["artistId"],
                "name": artist["name"],
                "profile": artist.get("profilePageUrl", None),
                "role": "/".join([role_map[role] for role in artist["artistTypeList"]])
            }
        )

    print(f"fetched: {res["title"]["name"]}")
    return res

def import_title_data(connection: sqlite3.Connection, title: dict, subtitles: List[dict], artists: List[dict]) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute(
        "INSERT OR REPLACE INTO title VALUES (:id, :name, :synopsis, :thumbnail, :banner);",
        title
    )
    cursor.executemany(
        f"INSERT OR REPLACE INTO subtitle VALUES ({title["id"]}, :id, :name, :date, :thumbnail, :comment);",
        subtitles
    )
    cursor.executemany(
        "INSERT OR REPLACE INTO artist VALUES (:id, :name, :profile);",
        artists
    )
    cursor.executemany(
        f"INSERT OR REPLACE INTO title_artist VALUES ({title["id"]}, :id, :role);",
        artists
    )

    # @TODO images
    connection.commit()
    print(f"imported: {title["name"]}")