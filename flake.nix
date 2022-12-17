{
  description = "Nix flake for menta";
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; };
    in rec {
      devShell = with pkgs; let
        pythonEnv = pkgs.python3.withPackages (ps:
          [
            ps.cryptography
            ps.lxml
            ps.pylint
            ps.qrcode
            ps.reportlab
            ps.svglib
            ps.xmltodict
          ]
        );
      in mkShell {
        buildInputs = [
          pythonEnv
        ];
      };
    }
  );
}
