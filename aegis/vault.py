import base64
import json
import secrets
import uuid
from aegis.icons import IconGenerator
from base64 import b32encode, b64encode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import cryptography
backend = default_backend()

class VaultError(Exception):
    pass

def _decrypt(ct, key, nonce, safe=True):
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend)
    decryptor = cipher.decryptor()
    pt = decryptor.update(ct[:len(ct) - 16])
    if safe:
        pt += decryptor.finalize_with_tag(ct[len(ct) - 16:])
    return pt

def decrypt_vault(data, password, safe=True):
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
        params = slot["key_params"]
        try:
            ct = bytes.fromhex(slot["key"]) + bytes.fromhex(params["tag"])
            master_key = _decrypt(ct, key, bytes.fromhex(params["nonce"]), safe=safe)
        except cryptography.exceptions.InvalidTag:
            pass

    if master_key is None:
        raise VaultError("unable to decrypt the master key with the given password")

    # decode the base64 vault contents
    content = base64.b64decode(data["db"])

    # decrypt the vault contents using the master key
    params = header["params"]
    db = _decrypt(content + bytes.fromhex(params["tag"]), master_key, bytes.fromhex(params["nonce"]), safe=safe)
    return db.decode("utf-8", errors="strict" if safe else "replace")

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

class VaultGenerator:
    def __init__(self, no_icons=False):
        self._no_icons = no_icons
        self._icon_gen = IconGenerator()

    def generate(self, entry_count=20):
        entries = []
        for i in range(entry_count):
            entries.append(self.generate_entry())

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

    def generate_entry(self):
        # generate a random icon and render it to PNG
        icon = self._icon_gen.generate_random()

        # generate a random 128-bit secret
        secret = b32encode(secrets.token_bytes(16)).decode("utf-8").rstrip("=")
        entry = {
            "type": "totp",
            "uuid": str(uuid.uuid4()),
            "name": secrets.choice(_names),
            "issuer": icon.title,
            "icon": None if self._no_icons else b64encode(icon.render_png()).decode("utf-8"),
            "info": {
                "secret": secret,
                "algo": "SHA1",
                "digits": 6,
                "period": 30
            }
        }

        return entry
