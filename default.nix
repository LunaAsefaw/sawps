with import <nixpkgs> { };
# See https://discourse.nixos.org/t/how-to-install-rstudio-wrapper-packages-declaratively/30269/7
let
  pkgs = import <nixpkgs> {};
  RStudio-with-my-packages = rstudioWrapper.override{
      packages = with rPackages; [ tidyverse snakecase ]; };
in pkgs.mkShell rec {
  name = "R";
  buildInputs = [
    RStudio-with-my-packages
  ];

}

