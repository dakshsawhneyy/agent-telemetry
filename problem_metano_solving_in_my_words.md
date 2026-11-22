# problem:
1. Nobody knows who did what. If an agent deletes something, which agent was it, under which identity, using which tool, on which data?
2. Agents go beyond their job. An agent meant to read a file ends up touching a password file.
3. The tools that watch agents need access to your cloud. If that connection is sloppy (stored keys, weak trust), the monitoring tool becomes the hole.

4. ## How it connects to Metano:
Their public descriptions say Hive links agent tasks, identities, tools, data and actions.

So:
- Our graph (agent → identity → tool → data → action) is us making that sentence concrete.
- The detection rule is the smallest possible version of "spot an agent acting outside its remit."
- The secure connector is the part a security-company founder would worry about, because their product has to connect into customers' clouds.

#### So what i am trying to build?
#### To know about what's Metano working with

Scene 1, normal agent. A script runs as agent-A. It reads a file, calls an API, and does nothing else. Each action sends an event, and the graph shows a clean chain.

Scene 2, bad agent. agent-B is only allowed to read files, but it also tries to read the fake secret. The detection rule fires and the graph shows that edge in red.

Scene 3, no stored keys. We show there are no AWS keys on the machine. The agent proved who it was and got credentials that die in about 15 minutes.

Scene 4, External ID. A "vendor" tries to assume a role in a "customer" account. Without the External ID it's rejected. With it, it works

---

│      Piece       │            What it is            │             The idea behind it              │

│ Toy agent        │ A Python script with 3 tools     │ Stands in for a real agent. Nothing smart   │
│                  │                                  │ is needed.                                  │

│ Event            │ One JSON line per action         │ The "who, what tool, what data, what        │
│                  │                                  │ action" record. This is the telemetry.      │

│ Short-lived      │ Agent shows an identity token,   │ Nothing long-lived exists to be stolen.     │
│ credentials      │ AWS gives temporary keys         │ This is workload identity federation.       │

│ Ingestion        │ A small AWS endpoint that        │ Only accepts requests signed with the       │
│ endpoint         │ receives events                  │ temporary keys.                             │

│ Detection rule   │ Compares each event to           │ Runs on the receiving side, so an agent     │
│                  │ policy.json                      │ can't mark its own homework.                │

│ Graph            │ Prints agent → identity → tool → │ Makes it visible in a video.                │
│                  │  data → action                   │                                             │

│ External ID demo │ Role in a "customer" account     │ Stops the confused deputy attack (below).   │
│                  │ that demands a secret ID         │                                             │


