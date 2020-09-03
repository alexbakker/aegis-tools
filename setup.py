from setuptools import find_packages, setup

__version__ = "0.2.1"

setup(
    name="aegis-tools",
    version=__version__,
    description="A collection of developer tools for Aegis Authenticator",
    author="Alexander Bakker",
    author_email="ab@alexbakker.me",
    url="https://github.com/alexbakker/aegis-tools",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "cryptography",
        "lxml",
        "qrcode",
        "reportlab",
        "svglib>=0.9.0",
        "xmltodict"
    ],
    entry_points={
        "console_scripts": [
            "aegis-tools=aegis_tools:main",
        ],
    },
    license="GPLv3"
)
