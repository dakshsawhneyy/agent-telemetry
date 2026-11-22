# agent-telemetry

A small experiment i did after reading about Hive. This is not "my version of Metano", i dont know how Metano works inside. Its just me trying to understand the problem by building a tiny thing.

**Status: still planning, nothing is built yet. I will update this file when its done.**

Demo video: (will add link, ~60-90 sec)

## What it does

- A toy agent (just a python script) does 3 things: reads a file, calls an API, and touches a fake "secret".
- Every action sends out an event: which agent, which identity, which tool, what data.
- Events go to a cloud endpoint using short lived credentials only. No keys stored anywhere.
- One detection rule: alert if an agent uses a tool its not allowed to, or touches a secret it shouldnt.
- A simple graph that shows agent -> identity -> tool -> data -> action. The bad one is marked red.

There is also a second small demo about connecting to someone elses AWS account safely (cross-account role + External ID). This is a pattern i explored, not something i claim a specific company does.

## What threat it is about

1. **Long lived keys.** Static keys get leaked in git, logs, ci. Here the agent swaps an identity token for temporary credentials instead (workload identity federation).
2. **Agents doing more then they should.** Agents call tools and read data nobody planned for. The rule here is a very basic version of "who did what, and were they allowed?"
3. **Confused deputy.** If one vendor connects to many customer accounts, someone could trick the vendor to act on another customers account. A unique External ID in the role trust policy stops this. In the demo the assume-role call fails without the ID.

## What it does NOT do

- Its not a product, and its not how Metano / Hive is built. Anything i say about them is my guess.
- The agent is a script, not a real LLM agent.
- The secret is a fake file. No real credentials used, ever.
- Detection is only 2 hardcoded rules. No learning, no tuning, no alert routing.
- A bad agent could lie in its own events. A real system must capture actions outside the agent.
- Vendor and customer are both simulated in one AWS account, so it shows the idea only, not real multi-customer setup.
- Nothing about scale, privacy, data retention or other clouds.

## What i would learn next

- Capture actions at the tool / MCP gateway, instead of trusting the agent to report itself.
- Permissions per task, not per agent.
- Detect when an agent behaves different from its normal (not only a fixed allow list).
- Join events from agents, humans and service accounts into one graph.
- How teams really roll out workload identity in production.

## Folders (planned)

```
agent/    toy agent + policy.json (allowed tools)
events/   event format
ingest/   cloud endpoint + temp credentials
detect/   the detection rules
graph/    prints the graph
onboard/  cross-account role + External ID demo
```

## How to run

Todo, after i build it.
