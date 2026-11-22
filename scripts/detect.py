"""
detect.py - the detection rules.

Reads events.jsonl and policy.json, and returns alerts.

Rule 1: agent used a tool that is not in its allowed_tools list.
Rule 2: agent touched data that is not in its allowed_data patterns
        (we call it a "secret touch" when the data lives under secrets/).

Both rules are checked on the receiving side, not inside the agent.
"""
import json
from pathlib import Path
from fnmatch import fnmatch  # simple wildcard match: "data/*" matches "data/notes.txt"


ROOT = Path(__file__).resolve().parent.parent  # project folder


def load_events(path=None):
    path = path or ROOT / "events.jsonl"
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def check_event(event, policy):
    """Return a list of problems for one event (empty list = fine)."""
    rules = policy[event["agent"]]
    problems = []

    if event["tool"] not in rules["allowed_tools"]:
        problems.append("TOOL_NOT_ALLOWED")

    if not any(fnmatch(event["data"], pattern) for pattern in rules["allowed_data"]):
        if event["data"].startswith("secrets/"):
            problems.append("SECRET_TOUCHED")
        else:
            problems.append("DATA_NOT_ALLOWED")

    return problems


def detect(events, policy):
    """Return the events with a 'problems' list added to each."""
    results = []
    for e in events:
        results.append({**e, "problems": check_event(e, policy)})
    return results
