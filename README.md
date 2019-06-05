# aegis-tools

__aegis-tools__ is a collection of developer tools for Aegis Authenticator.

## Installation

This package is not available on PyPi, so you need to clone the repository and
install it manually.

```sh
git clone --recursive-submodules https://github.com/alexbakker/aegis-tools
cd aegis-tools && pip install --user .
```

## Usage

The only useful tool for users is __decrypt-vault__. It can decrypt an Aegis
vault given a password.

```sh
aegis-tools decrypt-vault --input vault.json > db.json
```

Developers may find the __gen-vault__ tool useful. It generates vault files for use
in Aegis with random issuers, names, icons, secrets, etc.

```sh
aegis-tools gen-vault > vault.json
```

It also has an experimental tool for generating a collection of SVG icons for
well-known web services based on the [Simple Icons](https://simpleicons.org/)
icon collection.

```sh
DIR=$(mktemp -d)
aegis-tools gen-icons --output "${DIR}"
echo $DIR
```
