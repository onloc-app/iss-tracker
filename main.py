import argparse
import time
from typing import Any, Dict

import requests

API_ENDPOINT = "/api/locations"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live ISS Tracker for Onloc",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "baseurl",
        help="Onloc API base URL (e.g. http://localhost:4000 or https://onloc.example.com)",
    )
    parser.add_argument(
        "token",
        help="Bearer token for Onloc authentication",
    )
    parser.add_argument(
        "deviceid",
        type=int,
        help="Device ID to report as",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=8,
        help="Polling interval in seconds (default: 8)",
    )
    return parser.parse_args()


def get_iss_location() -> Dict[str, Any]:
    url = "https://api.wheretheiss.at/v1/satellites/25544"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_location_payload(iss_data: Dict[str, Any], device_id: int) -> Dict[str, Any]:
    payload = {
        "device_id": device_id,
        "latitude": iss_data["latitude"],
        "longitude": iss_data["longitude"],
    }
    return payload


def post_to_onloc(base_url: str, token: str, payload: Dict[str, Any]) -> None:
    url = base_url + API_ENDPOINT
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()


def main() -> None:
    args = parse_args()

    print("Tracker started")
    print("Press Ctrl+C to stop")

    while True:
        try:
            iss_data = get_iss_location()
            payload = build_location_payload(iss_data, args.deviceid)
            post_to_onloc(args.baseurl, args.token, payload)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
