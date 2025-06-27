{
  description = "";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  inputs.nix-jetbrains-plugins.url = "github:theCapypara/nix-jetbrains-plugins";

  outputs = { self, nixpkgs,nix-jetbrains-plugins, ... } @ inputs: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages =  [
        pkgs.nodejs
        
      ];
    };
  };
}
