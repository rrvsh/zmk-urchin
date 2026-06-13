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

            # nice-view-gem v0.3.0 builds cleanly in ZMK's official container,
            # but nixpkgs currently supplies a much newer arm-none-eabi GCC
            # which treats a few missing minimal-libc declarations as fatal.
            extraCmakeFlags = [
              "-DCMAKE_C_FLAGS=-Wno-implicit-function-declaration"
              "-DCONFIG_NEWLIB_LIBC=y"
            ];

            meta = {
              description = "ZMK firmware for Urchin with nice!nano v2 and nice!view/gem";
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
              name = "urchin-firmware";
              board = "nice_nano_v2";
              shield = "urchin_%PART% nice_view_adapter nice_view_gem";
              enableZmkStudio = true;
            }
          );

          settings-reset = builders.buildKeyboard (
            common
            // {
              name = "urchin-settings-reset";
              board = "nice_nano_v2";
              shield = "settings_reset";
            }
          );

          all = pkgs.runCommand "urchin-zmk-firmware" { } ''
            mkdir -p $out
            cp ${firmware}/zmk_left.uf2 $out/urchin_left-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2
            cp ${firmware}/zmk_right.uf2 $out/urchin_right-nice_view_adapter-nice_view_gem-nice_nano_v2-zmk.uf2
            cp ${settings-reset}/zmk.uf2 $out/settings_reset-nice_nano_v2-zmk.uf2
          '';

          flash = zmk-nix.packages.${system}.flash.override { inherit firmware; };
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
            packages = [ pkgs.just ];
          };
        }
      );
    };
}
