import json
import random
import re
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ALBUMS_FILE = BASE_DIR / "albums.json"


def normalise_google_photo_url(url):
    if "/pw/" not in url:
        return None

    base = url.split("=")[0]

    return f"{base}=w1920-h1080-no"


def get_album_photos(album_url):
    request = urllib.request.Request(
        album_url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        html = response.read().decode(
            "utf-8",
            errors="ignore",
        )

    pattern = (
        r'https://lh3\.googleusercontent\.com/[^"\\]+'
    )

    raw_urls = re.findall(
        pattern,
        html,
    )

    photos = []

    for url in raw_urls:
        photo_url = normalise_google_photo_url(
            url
        )

        if photo_url:
            photos.append(photo_url)

    return list(dict.fromkeys(photos))


def get_all_photos():
    with open(
        ALBUMS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)

    photos = []

    for album_url in config.get(
        "albums",
        [],
    ):
        try:
            photos.extend(
                get_album_photos(album_url)
            )

        except Exception:
            pass

    photos = list(
        dict.fromkeys(photos)
    )

    random.shuffle(photos)

    return photos


if __name__ == "__main__":
    photos = get_all_photos()

    print(
        f"Found {len(photos)} photos."
    )