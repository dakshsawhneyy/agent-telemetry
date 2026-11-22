┌──────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│          Script          │                               What it does                               │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ policy.json              │ The rule list: which tools and data each agent may use.                  │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│                          │ The toy agent. It does small jobs and writes one event line for each     │
│ agent.py                 │ into events.jsonl. (I see you trimmed a comment block in it. The code is │
│                          │  the same.)                                                              │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ detect.py                │ Reads the events and checks them against policy.json. Flags tool misuse  │
│                          │ and secret/data access that isn't allowed.                               │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ graph.py                 │ Prints each event as agent → identity → tool → data → action, green if   │
│                          │ fine and red if flagged.                                                 │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ run_demo.py              │ Runs everything in order: agent-A (good), agent-B (bad), detection,      │
│                          │ graph.                                                                   │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ data/notes.txt           │ A harmless file the agents read.                                         │
├──────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ secrets/fake_api_key.txt │ The fake secret. Nothing real.                                           │
└──────────────────────────┴──────────────────────────────────────────────────────────────────────────┘