"""Spike: measure live payload size for the target parks (not production code)."""
# A "spike" is a quick experiment to answer one question before building the real thing.
# Here the question is: "How much data will we download and store if we poll every park
# every 5 minutes?" The answer helps decide how to store the data (e.g. whether to gzip it).

# --- Imports ---
import gzip   # standard library: compresses bytes so we can estimate storage savings
import json   # standard library: turns a JSON string/bytes into Python dicts and lists
from pathlib import Path  # standard library: builds file paths that work on any OS

import requests  # third-party: makes HTTP requests (installed in the venv)
import yaml      # third-party (PyYAML): reads the config/parks.yaml file

# --- Constants (UPPER_CASE is the Python convention for values that never change) ---
BASE_URL = "https://api.themeparks.wiki/v1"  # the public API that serves live wait times
# Identifies our script to the API owners, so they know who is calling and can contact us.
USER_AGENT = "orlando-wait-times/0.1 (+https://github.com/vitinhoBig/orlando-wait-times)"
# __file__ is this script's path. resolve() makes it absolute, .parent is the scripts/ folder,
# and the second .parent is the project root. From there we go into config/parks.yaml.
CONFIG = Path(__file__).resolve().parent.parent / "config" / "parks.yaml"
# 24 hours * 60 minutes = 1440 minutes per day; // 5 is integer division -> 288 polls per day.
POLLS_PER_DAY = 24 * 60 // 5  # one poll every 5 minutes


def load_parks():
    """Read parks.yaml and return the list of parks (each has a 'name' and an 'id')."""
    # `with` closes the file automatically, even if an error happens while reading.
    with open(CONFIG) as f:
        # safe_load only builds plain Python types (safer than yaml.load on untrusted files).
        # The file looks like {"parks": [{"name": ..., "id": ...}, ...]}, so we return the list.
        return yaml.safe_load(f)["parks"]


def fetch_live(park_id):
    """Download the live data for one park and return it as raw bytes."""
    response = requests.get(
        f"{BASE_URL}/entity/{park_id}/live",  # f-string: inserts the park's id into the URL
        headers={"User-Agent": USER_AGENT},   # tell the API who we are
        timeout=10,  # give up after 10 seconds so the script never hangs forever
    )
    # If the server answered with an error (404, 500, ...), raise an exception now
    # instead of silently continuing with bad data.
    response.raise_for_status()
    # .content is the raw bytes exactly as received. We want bytes (not .json()) because
    # we are measuring the real download size and need bytes to feed into gzip.
    return response.content


def main():
    # Chained assignment: all three running totals start at 0.
    total_raw = total_gz = total_attr = 0
    # Table header. In an f-string, `:<28` left-aligns in 28 characters and `:>10` right-aligns
    # in 10, which keeps the columns lined up.
    print(f"{'park':<28}{'raw KB':>10}{'gzip KB':>10}{'attractions':>13}")

    for park in load_parks():
        raw = fetch_live(park["id"])  # bytes as downloaded
        gz = gzip.compress(raw)       # the same data compressed; compare its size to `raw`
        data = json.loads(raw)        # parse the JSON bytes into a Python dict
        # Count only the entries that are rides. The generator adds 1 for every entry in
        # "liveData" whose "entityType" is "ATTRACTION" (other types: shows, restaurants...).
        # .get(..., []) avoids a crash if the key is missing.
        n_attr = sum(1 for entry in data.get("liveData", []) if entry.get("entityType") == "ATTRACTION")

        # Divide bytes by 1024 to get KB; `:>10.1f` = right-aligned float with 1 decimal.
        print(f"{park['name']:<28}{len(raw)/1024:>10.1f}{len(gz)/1024:>10.1f}{n_attr:>13}")
        # Add this park's numbers to the running totals.
        total_raw += len(raw)
        total_gz += len(gz)
        total_attr += n_attr

    print("-" * 61)  # a separator line made of 61 dashes
    # Total size of ONE round of polling across all parks.
    print(f"{'TOTAL per poll':<28}{total_raw/1024:>10.1f}{total_gz/1024:>10.1f}{total_attr:>13}")
    # Projection: multiply one poll's size by polls per day. 1024**2 converts bytes to MB.
    print(f"\nProjection at {POLLS_PER_DAY} polls/day:")
    print(f"  raw : {total_raw * POLLS_PER_DAY / 1024**2:8.1f} MB/day")
    print(f"  gzip: {total_gz * POLLS_PER_DAY / 1024**2:8.1f} MB/day")
    # `:,d` adds thousands separators. One row per attraction per poll would be stored.
    print(f"  rows: {total_attr * POLLS_PER_DAY:8,d} attraction rows/day")


# This runs main() only when you execute the file directly (python spike_payload.py).
# If another file imports this one, __name__ is different and main() does NOT run.
if __name__ == "__main__":
    main()
