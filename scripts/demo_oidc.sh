#!/usr/bin/env bash
# demo_oidc.sh - short commands for the screen recording (run in WSL / bash).
#
# Set your role once BEFORE recording (and clear the screen after):
#   export ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/agent-event-sender
#
# Then:
#   ./scripts/demo_oidc.sh nokeys     -> shows there are no AWS keys stored on this machine
#   ./scripts/demo_oidc.sh agent-A    -> token -> AWS -> temporary credentials (works)
#   ./scripts/demo_oidc.sh agent-X    -> an agent AWS does not know: rejected
#
# The secret keys that AWS returns are NEVER printed. Only who/role/expiry are shown,
# and the 12 digit account id is hidden with ************.

set -u
REGION="${AWS_REGION:-ap-south-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mask() { sed -E 's/[0-9]{12}/************/g'; }

if [ "${1:-}" = "nokeys" ]; then
  echo '$ ls ~/.aws/credentials'
  ls ~/.aws/credentials 2>&1 | mask
  echo '$ env | grep AWS_ACCESS_KEY'
  env | grep AWS_ACCESS_KEY || echo "(nothing - no access keys in the environment)"
  exit 0
fi

AGENT="${1:?usage: demo_oidc.sh nokeys | agent-A | agent-B | agent-X}"
: "${ROLE_ARN:?set ROLE_ARN first (see top of this file)}"

echo "1) $AGENT makes a signed identity token (valid 10 min, nothing stored)"
TOKEN="$(python3 "$HERE/issuer.py" token "$AGENT" "summarise notes")"
echo "   token starts with: ${TOKEN:0:20}..."

echo
echo "2) Asking AWS to swap the token for temporary credentials"
aws sts assume-role-with-web-identity \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$AGENT-demo" \
  --web-identity-token "$TOKEN" \
  --duration-seconds 900 \
  --region "$REGION" \
  --query '{Who:SubjectFromWebIdentityToken,Role:AssumedRoleUser.Arn,ExpiresAt:Credentials.Expiration}' \
  --output table 2>&1 | mask
