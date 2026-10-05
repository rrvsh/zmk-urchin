{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    zmk-nix = {
      url = "github:lilyinstarlight/zmk-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      zmk-nix,
    }:
    let
      forAllSystems = nixpkgs.lib.genAttrs (nixpkgs.lib.attrNames zmk-nix.packages);
      zmkSource =
        lib:
        lib.sourceFilesBySuffices self [
          ".board"
          ".cmake"
          ".conf"
          ".defconfig"
          ".dts"
          ".dtsi"
          ".json"
          ".keymap"
          ".overlay"
          ".shield"
          ".yml"
          "_defconfig"
        ];
      zephyrDepsHash = "sha256-IhmzLaktf/F4cLvtVvZeL8v1/BDP/MQi/wM1uJpCpXI=";
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          builders = zmk-nix.legacyPackages.${system};
          common = {
            src = zmkSource pkgs.lib;
            config = "config";
            zephyrDepsHash = zephyrDepsHash;

            meta = {
              description = "ZMK firmware for Dolphin34 with the Cradio shield";
              license = pkgs.lib.licenses.mit;
              platforms = pkgs.lib.platforms.all;
            };
          };
        in
        rec {
          default = all;

          firmware = builders.buildSplitKeyboard (
            common
            // {
              name = "dolphin34-firmware";
              board = "nice_nano_v2";
              shield = "cradio_%PART%";
              enableZmkStudio = true;
            }
          );

          settings-reset = builders.buildKeyboard (
            common
            // {
              name = "dolphin34-settings-reset";
              board = "nice_nano_v2";
              shield = "settings_reset";
            }
          );

          all = pkgs.runCommand "dolphin34-zmk-firmware" { } ''
            mkdir -p $out
            cp ${firmware}/zmk_left.uf2 $out/dolphin34_left-nice_nano_v2-zmk.uf2
            cp ${firmware}/zmk_right.uf2 $out/dolphin34_right-nice_nano_v2-zmk.uf2
            cp ${settings-reset}/zmk.uf2 $out/settings_reset-nice_nano_v2-zmk.uf2
          '';

          update = zmk-nix.packages.${system}.update;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            inputsFrom = [ zmk-nix.devShells.${system}.default ];
            packages = [
              pkgs.just
              pkgs.python3
            ];
          };
        }
      );
    };
}
