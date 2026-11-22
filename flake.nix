{
  description = "Website development environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    devshell.url = "github:numtide/devshell";
  };

  outputs = { self, nixpkgs, flake-utils, devshell, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ devshell.overlays.default ];
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pillow
        ]);
      in
      {
        devShells.default = pkgs.devshell.mkShell {
          name = "website-dev";

          packages = with pkgs; [
            hugo
            pythonEnv
            git
          ];

          commands = [
            {
              name = "serve";
              help = "Start Hugo development server";
              command = "hugo server -D";
            }
            {
              name = "gen-favicons";
              help = "Generate favicons";
              command = "python3 scripts/generate-favicons.py";
            }
            {
              name = "gen-og-image";
              help = "Generate the share image (static/images/og.png)";
              command = "python3 scripts/generate-og-image.py";
            }
            {
              name = "check";
              help = "Build like CI and check the site";
              command = "python3 scripts/check-site.py";
            }
          ];

          env = [
            {
              name = "HUGO_ENV";
              value = "development";
            }
          ];
        };
      }
    );
}
