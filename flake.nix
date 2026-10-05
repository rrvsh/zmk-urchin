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
      zephyrDepsHash = "sha256-FJsXK7ctkQwkpQOxNWXOTSYySSMBNcyH8uj0xy0IV4o=";
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
          };
        in
        rec {
          default = all;

          urchin-firmware = builders.buildSplitKeyboard (
            common
            // {
              name = "urchin-firmware";
              board = "nice_nano_v2";
              shield = "urchin_%PART% nice_view_adapter nice_view_gem";
              enableZmkStudio = true;
              extraCmakeFlags = [
                "-DCMAKE_C_FLAGS=-Wno-implicit-function-declaration"
                "-DCONFIG_NEWLIB_LIBC=y"
              ];
              meta = {
                description = "ZMK firmware for Urchin with nice!nano v2 and nice!view/gem";
                license = pkgs.lib.licenses.mit;
                platforms = pkgs.lib.platforms.all;
              };
            }
          );

          dolphin34-firmware = builders.buildSplitKeyboard (
            common
            // {
              name = "dolphin34-firmware";
              board = "nice_nano_v2";
              shield = "cradio_%PART%";
              enableZmkStudio = true;
              meta = {
                description = "ZMK firmware for Dolphin34 with the Cradio shield";
                license = pkgs.lib.licenses.mit;
                platforms = pkgs.lib.platforms.all;
              };
            }
          );

          settings-reset = builders.buildKeyboard (
            common
            // {
              name = "settings-reset";
              board = "nice_nano_v2";
              shield = "settings_reset";
              meta = {
                description = "ZMK settings reset firmware";
                license = pkgs.lib.licenses.mit;
                platforms = pkgs.lib.platforms.all;
              };
            }
          );

          all = pkgs.runCommand "zmk-urchin-and-dolphin34-firmware" { } ''
            mkdir -p $out
            cp ${urchin-firmware}/zmk_left.uf2 $out/urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2
            cp ${urchin-firmware}/zmk_right.uf2 $out/urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2
            cp ${dolphin34-firmware}/zmk_left.uf2 $out/dolphin34_left-nice_nano_v2-zmk.uf2
            cp ${dolphin34-firmware}/zmk_right.uf2 $out/dolphin34_right-nice_nano_v2-zmk.uf2
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
