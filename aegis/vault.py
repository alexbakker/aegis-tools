import base64
import json
import os
import secrets
import sys
import uuid
from aegis.icons import IconGenerator
from base64 import b32encode,b64encode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import cryptography
backend = default_backend()

def decrypt_vault(data, password):
    # extract all password slots from the header
    header = data["header"]
    slots = [slot for slot in header["slots"] if slot["type"] == 1]

    # try the given password on every slot until one succeeds
    master_key = None
    for slot in slots:
        # derive a key from the given password
        kdf = Scrypt(
            salt=bytes.fromhex(slot["salt"]),
            length=32,
            n=slot["n"],
            r=slot["r"],
            p=slot["p"],
            backend=backend
        )
        key = kdf.derive(password.encode("utf-8"))

        # try to use the derived key to decrypt the master key
        cipher = AESGCM(key)
        params = slot["key_params"]
        try:
            master_key = cipher.decrypt(
                nonce=bytes.fromhex(params["nonce"]),
                data=bytes.fromhex(slot["key"]) + bytes.fromhex(params["tag"]),
                associated_data=None
            )
            break
        except cryptography.exceptions.InvalidTag:
            pass

    if master_key is None:
        die("error: unable to decrypt the master key with the given password")

    # decode the base64 vault contents
    content = base64.b64decode(data["db"])

    # decrypt the vault contents using the master key
    params = header["params"]
    cipher = AESGCM(master_key)
    db = cipher.decrypt(
        nonce=bytes.fromhex(params["nonce"]),
        data=content + bytes.fromhex(params["tag"]),
        associated_data=None
    )

    return json.loads(db.decode("utf-8"))

_names = [
    "Liam",
    "Emma",
    "Noah",
    "Olivia",
    "William",
    "Ava",
    "James",
    "Isabella",
    "Oliver",
    "Sophia",
    "Benjamin",
    "Charlotte",
    "Elijah",
    "Mia",
    "Lucas",
    "Amelia",
    "Mason",
    "Harper",
    "Logan",
    "Evelyn"
]

def generate_vault(entry_count=20):
    icon_gen = IconGenerator()

    entries = []
    for i in range(entry_count):
        # generate a random icon and render it to JPEG
        icon = icon_gen.generate_random()
        icon_s = b64encode(icon.render_png()).decode("utf-8")

        # generate a random 128-bit secret
        secret = b32encode(secrets.token_bytes(16)).decode("utf-8")

        entries.append({
            "type": "totp",
            "uuid": str(uuid.uuid4()),
            "name": secrets.choice(_names),
            "issuer": icon.title,
            "icon": icon_s,
            "info": {
                "secret": secret,
                "algo": "SHA1",
                "digits": 6,
                "period": 30
            }
        })

    return {
        "version": 1,
        "header": {
            "slots": None,
            "params": None
        },
        "db": {
            "version": 1,
            "entries": entries
        }
    }
