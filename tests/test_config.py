"""Sanity checks for config/parks.yaml."""
import uuid
from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "parks.yaml"


def load_parks():
    """Read parks.yaml and return the list of parks (each with "name" and "id")."""
    with open(CONFIG) as f:
        return yaml.safe_load(f)["parks"]


def test_has_eight_parks():
    assert len(load_parks()) == 8


def test_every_park_has_name_and_id():
    for park in load_parks():
        assert park.get("name"), f"park without name: {park}"
        assert park.get("id"), f"park without id: {park}"


def test_ids_are_unique():
    # Collects all the ids into a list and assert there are no duplicates
    ids = [park["id"] for park in load_parks()]
    assert len(ids) == len(set(ids))      #Checks if there are duplicate IDs found


def test_ids_are_valid_uuids():
    for park in load_parks():
        park_id = park.get("id")
        park_name = park.get("name", "Unknown Park")

        try:
            uuid.UUID(str(park_id))

        except ValueError:
            raise AssertionError(
                f"Invalid UUID for park '{park_name}': '{park_id}' is not a valid UUID string."
            ) from None