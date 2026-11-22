# Plan (draft, nothing built yet)

## Why im doing this
I want to show a founder a small working thing, in about 90 seconds, that i understand what Hive talks about (agents, identities, tools, data, actions) and one real security risk when a vendor connects to a customer cloud. Goal is a job conversation, not a product.

Success = they watch the video and think "ok this person thinks like a security person and can ship small things."
Not wanted = looking like a Metano clone or claiming stuff i dont know. Everything about how Metano works is only my guess, README says that.

## Two parts, dont mix them

| Part | Pieces | What it shows |
|---|---|---|
| A. Telemetry | toy agent, events, detection rule, graph | i can model agent -> identity -> tool -> data -> action and catch misuse |
| B. Secure connection | short lived creds (WIF), External ID | i understand keyless auth and confused deputy |

Part B is the one that makes me different. Part A is just to make it visible.

## Things to be careful about
- "WIF" is a Google term, External ID is an AWS thing. Using both clouds = more setup, messy demo. So AWS only (see decision 1).
- The "secret" is a fake canary file. Never a real key.
- Confused deputy needs two parties. I only have one account so i simulate vendor and customer as two roles. Say it in README.

## Options i thought about

**A. AWS only, real ingestion (my pick)**
Agent gets an OIDC token, calls STS AssumeRoleWithWebIdentity, gets 15 min creds, sends events to an endpoint (API Gateway + Lambda -> S3). Second flow: customer role needs sts:ExternalId, show it fails without and works with. More IAM work but most believable.

**B. GCP with real WIF, External ID only as a diagram**
WIF is natural but the External ID part cant run, so part B is weaker.

**C. All local, mock STS and mock IdP**
Free and runs anywhere but founder can see its fake. Keep as backup for the video if cloud setup goes bad.

## Rough design
```
toy agent --> event {agent, identity, tool, data, action, time}
   |                         |
   | OIDC token              | https, signed with temp creds
   v                         v
 STS assume role  --->  ingestion endpoint --> event store
                                                  |
                                  detection <-----+-----> graph
```
- Agent: python, 3 tools (read_file, call_api, read_secret). Each agent has identity + allowed list in policy.json.
- Event: one json line per action.
- Detection runs on the server side, agent should not judge itself.
- Rule 1: tool not in allowed list. Rule 2: secret touched without permission.
- Graph: printed tree or graphviz, bad edge in red.
- onboard.py: makes an External ID, shows trust policy, tries assume role with and without the ID.

## Steps
1. Local core first: agent, events, detection, graph. Two runs, one good one bad. No cloud.
2. Cloud ingestion with short lived creds. Prove no keys on disk.
3. External ID flow with the failing test.
4. README, diagram, 60-90 sec recording.

If time is short cut graph polish first. Dont cut step 2 or the README.

## Video script (60-90 sec)
1. 10s - README top, one line of what this is
2. 20s - run normal agent, show events + graph
3. 20s - run bad agent, alert fires, red edge
4. 20s - show no keys on disk, creds expire in minutes
5. 15s - External ID: fails without, works with

## Risks
- Overclaiming about Metano -> keep wording "a pattern i explored"
- Cloud setup takes too long -> backup option C
- AWS cost -> free tier, delete everything after recording
- Leaking account ids in the video -> use a throwaway account, check video before sharing

## Still open
1. ~~AWS only or GCP?~~ DECIDED: AWS only, with option C (local mock) as backup
2. Python ok? (i say yes)
3. Public github repo with video linked in README?
4. Any info on who the founder is / what Metano uses, to tailor it? (optional)
