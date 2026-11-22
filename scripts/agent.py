"""
agent.py - the toy agent.

It is NOT smart. It just runs a fixed list of steps (a "script").
The important part: every time it uses a tool, it writes an EVENT line
to events.jsonl saying who did what. That is the telemetry.

The agent does NOT say if the action was allowed. The detector decides that later,
so an agent can't mark its own homework.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent  # project folder, so paths work from anywhere
EVENTS_FILE = ROOT / "events.jsonl"


def load_policy():
    with open(ROOT / "policy.json") as f:
        return json.load(f)


def emit_event(agent, identity, task, tool, data, action):
    """Write one event (one json line) to the events file."""
    event = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent": agent,
        "identity": identity,
        "task": task,
        "tool": tool,
        "data": data,
        "action": action,
    }
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")




def read_file(path):
    with open(ROOT / path) as f:
        return f.read()


def call_api(url):
    # Faked on purpose, so the demo never breaks because of the network.
    return {"status": 200, "body": "fake api response"}


def read_secret(path):
    with open(ROOT / path) as f:
        return f.read()


TOOLS = {"read_file": read_file, "call_api": call_api, "read_secret": read_secret}

# What kind of "action" each tool counts as (this is the last box in the graph)
ACTION_OF = {"read_file": "read", "call_api": "call", "read_secret": "read"}


def run_agent(name, task, steps):
    """steps = list of (tool_name, target). Runs them one by one, emitting an event each."""
    policy = load_policy()
    identity = policy[name]["identity"]

    for tool_name, target in steps:
        TOOLS[tool_name](target)  # actually do the thing
        emit_event(name, identity, task, tool_name, target, ACTION_OF[tool_name])
        print(f"  {name} used {tool_name} on {target}")
