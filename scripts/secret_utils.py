import os
import time
import secrets
import jwt
from app.utils import read_secret

SECRETS_DIR = "secrets"

def create_secret(secret_name):

    os.makedirs(SECRETS_DIR, exist_ok=True)

    secret_path = os.path.join(SECRETS_DIR, secret_name)

    if os.path.exists(secret_path):
        return

    with open(secret_path, "w") as f:
        f.write(secrets.token_hex(32))


def generate_app_verification_token():
    secret_path = os.path.join(SECRETS_DIR, "app_verification_secret")
    with open(secret_path, "r") as f:
        secret = f.read()
        token = jwt.encode(
            {
                "iss": "our-app",
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600 * 24 * 30 * 12,  # 1 year
            },
            secret,
            algorithm="HS256"
        )

        return token
