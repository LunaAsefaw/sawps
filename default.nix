{ pkgs ? import <nixpkgs> {} }:

let
  #rev = "5272327b81ed355bbed5659b8d303cf2979b6953";
  #channel = fetchTarball "https://github.com/NixOS/nixpkgs/archive/${rev}.tar.gz";
  #config = {
  #  allowBroken = true;
  #};
  #pkgs = import channel { inherit config; };
  my-r-packages = with pkgs.rPackages; [
      tidyverse
  ];
  R-with-my-packages = pkgs.rWrapper.override{
    packages = my-r-packages;
  };
  RStudio-with-my-packages = pkgs.rstudioWrapper.override{ 
    packages = my-r-packages;
  };
  targetPkgs = pkgs: with pkgs; [
    
  ];
  env_vars = ''
    export EXTRA_CCFLAGS="-I/usr/include"
    
    # Points RCall to `libR.so`.
    export LD_LIBRARY_PATH="${pkgs.R}/lib/R/lib:$LD_LIBRARY_PATH"
    # Ensure that RCall uses the same R version as used by `libR.so`.
    # export R_HOME="${pkgs.R}/bin"

    # This does not add dependencies (recursively)!
    # Leaving the code since it was an interesting approach.
    # export R_LIBS_USER="$<removed open curly bracket here>
    #  (lib.concatMapStringsSep ":" (path: path + "/library") my-r-packages)
    # }"
    # export R_LIBS_USER=$R_LIBS_USER:$(R -e 'paste(.libPaths(), collapse=":")')

    # This seems to run after nixos-rebuild-switch, so R knows all the packages.
    # Do not set `R_LIBS_USER` since `using RCall` will overwrite it.
    LIBRARIES=$(Rscript -e 'paste(.libPaths(), collapse=":")')
    export R_LIBS_SITE="$(echo $LIBRARIES | cut -c6- | rev | cut -c2- | rev)"
  '';
  extraOutputsToInstall = ["man" "dev"];
  multiPkgs = pkgs: with pkgs; [ zlib ];



in pkgs.mkShell {
  name = "env";
  buildInputs = with pkgs; [
    R-with-my-packages
    RStudio-with-my-packages 
  ];
}
