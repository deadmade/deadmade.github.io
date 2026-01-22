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
            nodejs
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
              name = "fetch-projects";
              help = "Fetch pinned GitHub projects";
              command = "node scripts/fetch-projects.js";
            }
            {
              name = "gen-favicons";
              help = "Generate favicons";
              command = "python3 scripts/generate-favicons.py";
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
