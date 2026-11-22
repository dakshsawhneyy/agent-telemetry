# agent-telemetry

A small experiment i did after reading about Hive. This is not "my version of Metano", i dont know how Metano works inside. Its just me trying to understand the problem by building a tiny thing.

**Status: small prototype. Detection, keyless AWS access and sending events to S3 work. The External ID demo is NOT built. See "What works today" and "What is not done".**

Demo video: (link will be added)

## What it does

A toy agent does a few actions, every action leaves an event, and a rule checks if the agent was allowed to do it. Separately, i tried keyless access to AWS using my own tiny identity provider.

## What works today

**1. Detection (runs locally)**
- Toy agent (just a python script) reads a file, calls a fake API, or touches a fake "secret".
- Every action writes an event: agent, identity, task, tool, data, action.
- `policy.json` says what each agent is allowed to use.
- Two rules: tool not in allowed list, and data (or secret) not allowed.
- A printed graph `agent -> identity -> tool -> data -> action`. Bad lines are red.
- agent-A behaves, agent-B reads the secret, and gets flagged.

**2. Keyless AWS access (my own OIDC issuer)**
- `scripts/issuer.py` is a tiny token issuer. It signs a short token ("i am agent-A") with a private key that stays on my machine.
- The public key is published on GitHub Pages (`.well-known/`), same idea as what GitHub does for GitHub Actions.
- In AWS i added it as an OIDC identity provider, and made a role (`agent-event-sender`) that only accepts `sub` = agent-A or agent-B.
- Result: agent token -> AWS STS -> temporary credentials (about 15 min). A token for an unknown agent (agent-X) -> rejected.
- No AWS access keys are stored anywhere.

**3. Sending events to S3**
- `scripts/sender.py` uses those temporary credentials to upload each agent's events to `s3://<bucket>/events/<agent>/<time>.json`.
- The role can only do `s3:PutObject` on that `events/` prefix, nothing else.
- Detection still reads the local `events.jsonl`, not S3.

## What is not done (yet)

- **The External ID / confused deputy demo is not built.** It is only an idea i explored on paper, so it is in "what i would learn next" and not a feature.
- No video recorded yet (this line will change).

## What threat it is about

1. **Long lived keys.** Static keys get leaked in git, logs, ci. Here a short token is swapped for temporary credentials instead (workload identity federation).
2. **Agents doing more then they should.** Agents call tools and read data nobody planned for. The rule here is a very basic version of "who did what, and were they allowed?"
3. **Confused deputy** (not built, only described). If one vendor connects to many customer accounts, someone could trick the vendor to act on another customers account. A unique External ID in the role trust policy stops this.

## What it does NOT do

- Its not a product, and its not how Metano / Hive is built. Anything i say about them is my guess.
- The agent is a script, not a real LLM agent.
- The secret is a fake file. No real credentials used, ever.
- Detection is only 2 hardcoded rules, and it runs after the fact. No learning, no tuning, no alert routing, no blocking.
- Detection checks the allow list, not the task. It does not know if an action "fits the purpose" of the task.
- A bad agent could lie in its own events. A real system must capture actions outside the agent.
- My token issuer is a learning toy: one key, no rotation, no revocation.
- Nothing about scale, privacy, data retention or other clouds.

## What i would learn next

- Build the cross-account role + External ID demo (the confused deputy protection), so a vendor can safely connect into a customer account.
- Capture actions at the tool / MCP gateway, instead of trusting the agent to report itself.
- Judge actions against the task, not only a fixed allow list.
- Permissions per task, not per agent.
- Detect when an agent behaves different from its normal.
- Join events from agents, humans and service accounts into one graph.
- How teams really roll out workload identity in production.

## Folders

```
scripts/      agent.py, detect.py, graph.py, run_demo.py, issuer.py, demo_oidc.sh
policy.json   who may use which tools and data
data/         harmless file the agents read
secrets/      fake secret (not real)
.well-known/  public key files for AWS (published with GitHub Pages)
docs/         my own notes
```
The private key lives in `keys/` and is git-ignored. It is never committed.

## How to run

Detection demo (needs only python):
```
python scripts/run_demo.py
```

OIDC demo (needs AWS setup, bash/WSL, aws cli):
```
export ROLE_ARN=arn:aws:iam::<your-account-id>:role/agent-event-sender
./scripts/demo_oidc.sh nokeys     # shows no stored keys
./scripts/demo_oidc.sh agent-A    # works
./scripts/demo_oidc.sh agent-X    # unknown agent, rejected
```

To also send events to S3 when running the detection demo:
```
export ROLE_ARN=arn:aws:iam::<your-account-id>:role/agent-event-sender
export EVENT_BUCKET=<your-bucket-name>
python3 scripts/run_demo.py
```
(needs `pip install boto3 cryptography`)
To use your own AWS account you must make your own issuer keys (`python scripts/issuer.py init`), publish the `.well-known` files, and change the URL inside `scripts/issuer.py`.
