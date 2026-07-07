from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime
from client import WebClient
from schema import DatabaseClient

MOBILE_SECRET = ""
MOBILE_AGENT = ""
DESKTOP_AGENT = ""

def pull_data(client: WebClient, media_root: Path, title_id: int) -> tuple:
    title_desktop = client.get_title_desktop(title_id)
    title_mobile = client.get_title_mobile(title_id)

    client.save_media(title_desktop["thumbnailUrl"], media_root / f"{title_id}/thumbnail.jpg")
    client.save_media(title_mobile["title"]["illustCardUrl"], media_root / f"{title_id}/banner.png")

    title = {
        "id": title_desktop["titleId"],
        "name": title_desktop["titleName"],
        "synopsis": title_desktop["synopsis"]
    }

    artists = []
    role_map = {
        "ARTIST_WRITER": "글",
        "ARTIST_PAINTER": "그림",
        "ARTIST_NOVEL_ORIGIN": "원작"
    }

    for artist in title_desktop["communityArtists"]:
        artists.append({
            "id": artist["artistId"],
            "name": artist["name"],
            "profile": artist.get("profilePageUrl"),
            "role": "/".join([role_map[role] for role in artist["artistTypeList"]])
        })

    subtitles = []
    subtitle_info = client.get_subtitle_list(title_id)

    for subtitle in subtitle_info:
        date = datetime.strptime(subtitle["serviceDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
        comment = client.get_author_comment(title_id, subtitle["no"])
        comment = next((post for post in comment["postList"] if post["type"] == "COMMENT"), {})
        client.save_media(subtitle["thumbnailUrl"], media_root / f"{title_id}/thumbnails/{subtitle['no']}.jpg")

        subtitles.append({
            "id": subtitle["no"],
            "date": int(date.timestamp()),
            "image_cnt": 0, # @TODO import actual images
            "name": subtitle["subtitle"],
            "comment": comment.get("content")
        })

    return title, artists, subtitles

def push_data(client: DatabaseClient, title: list, artists: list, subtitles: list):
    cursor = client.cursor()

    cursor.execute("""
        INSERT INTO title
        VALUES (:id, :name, :synopsis)
        ON CONFLICT(id)
        DO UPDATE SET
            name = excluded.name,
            synopsis = excluded.synopsis;
        """,
        title
    )
    cursor.executemany("""
        INSERT INTO artist
        VALUES (:id, :name, :profile)
        ON CONFLICT(id)
        DO UPDATE SET
            name = excluded.name,
            profile = excluded.profile;
        """,
        artists
    )
    cursor.executemany(f"""
        INSERT OR REPLACE INTO title_artist
        VALUES ({title['id']}, :id, :role);
        """,
        artists
    )
    cursor.executemany(f"""
        INSERT OR REPLACE INTO subtitle
        VALUES ({title['id']}, :id, :date, :image_cnt, :name, :comment);
        """,
        subtitles
    )

if __name__ == "__main__":
    arguments = ArgumentParser()

    arguments.add_argument("-t", "--title-id", type=int, required=True)
    arguments.add_argument("-m", "--media-root", type=Path, required=True)
    arguments.add_argument("-d", "--db-path", type=Path, required=True)
    arguments = arguments.parse_args()

    with WebClient(
        mobile_secret=MOBILE_SECRET.encode("utf-8"),
        mobile_agent=MOBILE_AGENT,
        desktop_agent=DESKTOP_AGENT) as client:
        title, artists, subtitles = pull_data(client, arguments.media_root, arguments.title_id)

    with DatabaseClient(db_path=arguments.db_path) as client:
        push_data(client, title, artists, subtitles)
        client.commit()