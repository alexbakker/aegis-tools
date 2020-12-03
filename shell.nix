with import <nixpkgs> {};

(python3.withPackages(
	ps: [
		ps.cryptography
		ps.lxml
		ps.pylint
		ps.qrcode
		ps.reportlab
		ps.svglib
		ps.xmltodict
	]
)).env
