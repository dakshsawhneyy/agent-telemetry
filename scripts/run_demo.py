"""
run_demo.py - runs the whole stage 1 story, start to end.

  python run_demo.py
"""
import os
import json

from agent import run_agent, EVENTS_FILE, ROOT
from detect import load_events, detect
from graph import print_graph
from sender import send_events

# start fresh every run
if os.path.exists(EVENTS_FILE):
    os.remove(EVENTS_FILE)

print("== Running agents ==")

# agent-A behaves: only uses what it is allowed to
run_agent("agent-A", "summarise notes", [
    ("read_file", "data/notes.txt"),
    ("call_api", "api/summary"),
])

# agent-B misbehaves: reads a secret two ways
run_agent("agent-B", "summarise notes", [
    ("read_file", "data/notes.txt"),             # fine
    ("read_file", "secrets/fake_api_key.txt"),   # allowed tool, but data not allowed
    ("read_secret", "secrets/fake_api_key.txt"), # tool not allowed AND data not allowed
])

print("\n== Sending events to AWS (short-lived credentials, no stored keys) ==")
all_events = load_events()
for agent_name in ("agent-A", "agent-B"):
    send_events(agent_name, [e for e in all_events if e["agent"] == agent_name])

print("\n== Detection ==")
with open(ROOT / "policy.json") as f:
    policy = json.load(f)

results = detect(load_events(), policy)
print_graph(results)

alerts = [r for r in results if r["problems"]]
print(f"\n{len(alerts)} alert(s) out of {len(results)} events.")
