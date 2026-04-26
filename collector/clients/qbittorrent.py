import os
import requests
from dotenv import load_dotenv

load_dotenv()

QB_HOST = os.getenv("QB_HOST", "http://localhost:8080")
QB_USER = os.getenv("QB_USER", "admin")
QB_PASS = os.getenv("QB_PASS", "adminadmin")


def get_upload_stats() -> list[dict]:
    with requests.Session() as session:
        _login(session)
        return _get_torrents(session)


def _login(session: requests.Session) -> None:
    resp = session.post(f"{QB_HOST}/api/v2/auth/login", data={
        "username": QB_USER,
        "password": QB_PASS,
    })
    resp.raise_for_status()
    if resp.text != "Ok.":
        raise RuntimeError(f"Login failed: {resp.text}")


def _get_torrents(session: requests.Session) -> list[dict]:
    resp = session.get(f"{QB_HOST}/api/v2/torrents/info")
    resp.raise_for_status()
    return [
        {
            "hash": t["hash"],
            "name": t["name"],
            "uploaded": t["uploaded"],
        }
        for t in resp.json()
    ]
