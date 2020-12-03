import argparse
import getpass
import io
import json
import os
import secrets
import zipfile
from collections import namedtuple
from qrcode import QRCode
from urllib.parse import urlencode, quote as urlquote

from aegis.icons import IconGenerator
from aegis.vault import decrypt_vault, VaultGenerator

def _write_output(output, data):
    if output != "-":
        with io.open(output, "w") as f:
            f.write(data)
    else:
        print(data)

def _gen_uri() -> str:
    entry = VaultGenerator(no_icons=True).generate_entry()

    params = {
        "secret": entry["info"]["secret"],
        "issuer": entry["issuer"],
        "algorithm": entry["info"]["algo"],
        "digits": entry["info"]["digits"],
        "period": entry["info"]["period"]
    }

    uri = "otpauth://totp/{}:{}?".format(urlquote(entry["issuer"]), urlquote(entry["name"]))
    return uri + urlencode(params)

def _do_icons(args):
    gen = IconGenerator()
    for icon in gen.generate_all():
        with open(os.path.join(args.output, icon.filename), "w") as f:
            f.write(icon.get_xml())

def _do_icon_pack(args):
    categories = [
        "Gaming",
        "Security",
        "Services",
        "Social",
        "Memes",
        "Ecommerce",
        "Financial",
        None
    ]

    pack = {
        "uuid": "6a371ea0-1178-4677-ae93-cda7a7a5b378",
        "name": "Alex's Icon Pack",
        "version": 1,
        "icons": []
    }

    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zipf:
        for icon in IconGenerator().generate_all():
            basename = os.path.basename(icon.filename)
            filename_zip = os.path.join("SVG", basename)
            zipf.writestr(filename_zip, icon.get_xml())
            pack["icons"].append({
                "filename": filename_zip,
                "category": secrets.choice(categories),
                "issuer": [os.path.splitext(basename)[0]]
                })
        pack["icons"].sort(key=lambda icon: icon["filename"])
        zipf.writestr("pack.json", json.dumps(pack, indent=4).encode("utf-8"))

def _do_vault(args):
    gen = VaultGenerator(no_icons=args.no_icons)
    vault = gen.generate(entry_count=args.entries)
    _write_output(args.output, json.dumps(vault, indent=4))

def _do_decrypt(args):
    with io.open(args.input, "r") as f:
        data = json.load(f)

    # ask the user for a password
    password = getpass.getpass()

    db = decrypt_vault(data, password)
    _write_output(args.output, json.dumps(db, indent=4))

def _do_qr(args):
    uri = _gen_uri()

    qr = QRCode()
    qr.add_data(uri)
    qr.print_ascii(invert=True)

def _do_uri(args):
    uri = _gen_uri()
    print(uri)

def main():
    parser = argparse.ArgumentParser(description="A collection of developer tools for Aegis Authenticator", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    icon_parser = subparsers.add_parser("gen-icons", help="Generate icons for Aegis based on simple-icons", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    icon_parser.add_argument("--output", dest="output", required=True, help="icon output folder")
    icon_parser.set_defaults(func=_do_icons)

    icon_pack_parser = subparsers.add_parser("gen-icon-pack", help="Generate an icon pack for Aegis based on simple-icons", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    icon_pack_parser.add_argument("--output", dest="output", required=True, help="icon pack output filename")
    icon_pack_parser.set_defaults(func=_do_icon_pack)

    vault_parser = subparsers.add_parser("gen-vault", help="Generate a random vault for use in the Aegis app", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    vault_parser.add_argument("--output", dest="output", default="-", help="vault output file ('-' for stdout)")
    vault_parser.add_argument("--entries", dest="entries", default=20, type=int, help="the amount of entries to generate")
    vault_parser.add_argument("--no-icons", dest="no_icons", action="store_true", help="do not generate entry icons")
    vault_parser.set_defaults(func=_do_vault)

    qr_parser = subparsers.add_parser("gen-qr", help="Generate a random QR code", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    qr_parser.set_defaults(func=_do_qr)

    uri_parser = subparsers.add_parser("gen-uri", help="Generate a random URI", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    uri_parser.set_defaults(func=_do_uri)

    decrypt_parser = subparsers.add_parser("decrypt-vault", help="Decrypt an Aegis vault", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    decrypt_parser.add_argument("--input", dest="input", required=True, help="encrypted Aegis vault file")
    decrypt_parser.add_argument("--output", dest="output", default="-", help="output file ('-' for stdout)")
    decrypt_parser.set_defaults(func=_do_decrypt)

    args = parser.parse_args()
    if args.func:
        args.func(args)
