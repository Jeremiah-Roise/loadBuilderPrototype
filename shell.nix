{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
	pyright
	pylint
	python311
	pkgs.vscode-langservers-extracted
    pkgs.bashInteractive
	pkgs.python311Packages.flask
	pkgs.sqlite
	pkgs.entr
  ];
}
