"""
sender.py - sends an agent's events to S3 using SHORT-LIVED credentials.

No AWS access keys are used or stored. The steps are:

  1. The agent makes a signed identity token      (issuer.py)
  2. AWS STS swaps the token for temp credentials (about 15 min, then they die)
  3. Those temp credentials upload the events to  s3://<bucket>/events/<agent>/<time>.json

It only runs if BOTH environment variables are set:
  ROLE_ARN       e.g. arn:aws:iam::<account-id>:role/agent-event-sender
  EVENT_BUCKET   the name of your S3 bucket
Optional: AWS_REGION (default ap-south-1)

If they are not set, it skips quietly, so the offline demo still works.
If AWS says no (wrong agent, wrong role...), it prints the reason and carries on.
"""
import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from issuer import make_token


def send_events(agent, events):
    role_arn = os.environ.get("ROLE_ARN")
    bucket = os.environ.get("EVENT_BUCKET")
    region = os.environ.get("AWS_REGION", "ap-south-1")

    if not role_arn or not bucket:
        print(f"  {agent}: S3 sending skipped (set ROLE_ARN and EVENT_BUCKET to turn it on)")
        return False

    try:
        # step 1 + 2: token -> temporary credentials (this call needs no AWS keys)
        token = make_token(agent, events[0]["task"] if events else None)
        sts = boto3.client("sts", region_name=region)
        creds = sts.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName=f"{agent}-sender",
            WebIdentityToken=token,
            DurationSeconds=900,
        )["Credentials"]

        # step 3: upload using ONLY the temporary credentials
        s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        key = f"events/{agent}/{stamp}.json"
        body = "\n".join(json.dumps(e) for e in events)
        s3.put_object(Bucket=bucket, Key=key, Body=body.encode())

        print(f"  {agent}: sent {len(events)} events to s3://{bucket}/{key}")
        print(f"           (credentials valid until {creds['Expiration']:%H:%M:%S} UTC, then useless)")
        return True

    except (ClientError, BotoCoreError) as err:
        print(f"  {agent}: NOT sent -> {err}")
        return False
