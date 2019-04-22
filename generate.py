#!/usr/bin/env python3

# this script depends on the 'xmltodict' package
# pip install xmltodict

import argparse
import io
import json
import os
import re
from collections import OrderedDict

import xmltodict

# https://github.com/simple-icons/simple-icons/blob/f69ea6f28a3c864c79421e962103ebebbda7bb70/scripts/utils.js#L6-L15
def _title_to_name(title):
    title = title.lower()

    expr = [
        (r"\+", "plus", 0),
        (r"^\.", "dot-", 1),
        (r"\.$", "-dot", 1),
        (r"\.", "-dot-", 0),
        (r"^&", "and-", 1),
        (r"&$", "-and", 1),
        (r"&", "-and-", 0),
        (r"[ !’]", "", 0)
    ]

    for e in expr:
        title = re.sub(e[0], e[1], title, count=e[2])

    return title

def main():
    parser = argparse.ArgumentParser(description="Decrypt an Aegis vault")
    parser.add_argument("--input", dest="input", required=True, help="location of the simple-icons repository")
    parser.add_argument("--output", dest="output", required=True, help="icon output folder")
    args = parser.parse_args()

    with io.open(os.path.join(args.input, "_data", "simple-icons.json"), "r") as f:
        icons = json.load(f)["icons"]

    for icon in icons:
        name = _title_to_name(icon["title"]) + ".svg"
        filename = os.path.join(args.input, "icons", name)
        with io.open(filename, "r") as f:
            xml = xmltodict.parse(f.read())

        svg = OrderedDict()
        for key, val in xml["svg"].items():
            if key == "path":
                svg["circle"] = {
                    "@cx": 12,
                    "@cy": 12,
                    "@r": 12,
                    "@fill": "#" + icon["hex"]
                }
                val["@transform"] = "translate(4.8, 4.8) scale(0.6)"
                val["@fill"] = "white"
            svg[key] = val

        xml["svg"] = svg
        with open(os.path.join(args.output, name), "w") as f:
            f.write(xmltodict.unparse(xml, pretty=True))

if __name__ == "__main__":
    main()
