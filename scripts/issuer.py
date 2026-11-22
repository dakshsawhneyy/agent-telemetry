"""
issuer.py - our tiny identity provider (token issuer).

Two commands:

  python scripts/issuer.py init
      Makes a key pair ONCE.
        - private key  -> keys/private.pem   (secret, never published, git-ignored)
        - public files -> .well-known/  (these get published on GitHub Pages
                                              so AWS can verify our tokens)

  python scripts/issuer.py token agent-A
      Prints a signed token (JWT) that says "I am agent-A".
      It expires in 10 minutes. Nothing is stored.

How AWS uses this:
  1. AWS downloads  <ISSUER>/.well-known/openid-configuration  and the public keys.
  2. You send it a token. AWS checks the signature with our PUBLIC key.
  3. If the token is good and matches the role's trust policy, AWS gives temp credentials.
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ISSUER = "https://dakshsawhneyy.github.io/agent-telemetry"   # must match AWS "Provider URL" exactly
AUDIENCE = "agent-telemetry"                            # must match AWS "Audience" exactly
KEY_ID = "agent-idp-key-1"
TOKEN_LIFETIME_SECONDS = 600                            # 10 minutes

ROOT = Path(__file__).resolve().parent.parent  # project folder
PRIVATE_KEY_PATH = ROOT / "keys" / "private.pem"
WELL_KNOWN_DIR = ROOT / ".well-known"


def b64url(data: bytes) -> str:
    """JWTs use base64 with - and _ instead of + and /, and no = padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def int_to_b64url(n: int) -> str:
    return b64url(n.to_bytes((n.bit_length() + 7) // 8, "big"))


def init():
    if os.path.exists(PRIVATE_KEY_PATH):
        print(f"{PRIVATE_KEY_PATH} already exists. Not overwriting (that would break the published key).")
        sys.exit(1)

    # 1. make the key pair
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    os.makedirs(ROOT / "keys", exist_ok=True)
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))

    # 2. the public key, in the JWKS format AWS understands
    numbers = key.public_key().public_numbers()
    jwks = {"keys": [{
        "kty": "RSA", "use": "sig", "alg": "RS256", "kid": KEY_ID,
        "n": int_to_b64url(numbers.n),
        "e": int_to_b64url(numbers.e),
    }]}

    # 3. the "discovery document": tells AWS where to find the keys
    discovery = {
        "issuer": ISSUER,
        "jwks_uri": f"{ISSUER}/.well-known/jwks.json",
        "response_types_supported": ["id_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
    }

    os.makedirs(WELL_KNOWN_DIR, exist_ok=True)
    with open(f"{WELL_KNOWN_DIR}/jwks.json", "w") as f:
        json.dump(jwks, f, indent=2)
    with open(f"{WELL_KNOWN_DIR}/openid-configuration", "w") as f:
        json.dump(discovery, f, indent=2)

    # GitHub Pages hides folders starting with "." unless this empty file exists
    open(ROOT / ".nojekyll", "w").close()

    print("Done.")
    print(f"  private key (SECRET, stays local): {PRIVATE_KEY_PATH}")
    print("  commit .well-known/ and .nojekyll to master, then enable GitHub Pages")


def make_token(agent, task=None):
    """Build and sign a JWT. Returns the token string."""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT", "kid": KEY_ID}
    claims = {
        "iss": ISSUER,        # who issued this token
        "sub": agent,         # who it is about  (the trust policy checks this)
        "aud": AUDIENCE,      # who it is meant for (the trust policy checks this too)
        "iat": now,           # issued at
        "exp": now + TOKEN_LIFETIME_SECONDS,   # expires
    }
    if task:
        claims["task"] = task

    signing_input = (
        b64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + b64url(json.dumps(claims, separators=(",", ":")).encode())
    )
    signature = key.sign(signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())
    return signing_input + "." + b64url(signature)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "init":
        init()
    elif len(sys.argv) >= 3 and sys.argv[1] == "token":
        print(make_token(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
    else:
        print(__doc__)
