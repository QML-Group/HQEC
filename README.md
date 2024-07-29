# HQEC

This is the first "lite" version of HQEC operator push package. It contains an example of heptagon Steane Code.

## Dependencies

You'll need to have this software installed before carrying on:

- `git`
- `python` >= 3.9
- `pipx`

### Linux

```shell
apt-get update -qq -y
apt-get upgrade -qq -y
apt-get install git python3 pipx
pipx ensurepath
source ~/.bashrc
```

## Getting started

```shell
git clone https://github.com/QML-Group/HQEC
cd HQEC
poetry shell
poetry install
```