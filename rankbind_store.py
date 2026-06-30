import json
import os

FILE = os.path.join(os.path.dirname(__file__), "rankbinds.json")


def _load():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({}, f)
    with open(FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_bind(rank_id: int, role_id: int):
    data = _load()
    data[str(rank_id)] = role_id
    _save(data)


def remove_bind(rank_id: int):
    data = _load()
    data.pop(str(rank_id), None)
    _save(data)


def get_all_binds():
    return _load()