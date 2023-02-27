![TWC CLI](https://github.com/timeweb-cloud/twc/blob/master/artwork/logo.svg)

Timeweb Cloud Command Line Interface and simple SDK 💫

> [Документация на русском](https://github.com/timeweb-cloud/twc/blob/master/docs/ru/README.md) 🇷🇺

# Installation

```
pip install twc-cli
```

# Getting started

Get Timeweb Cloud [access token](https://timeweb.cloud/my/api-keys) and
configure **twc** with command:

```
twc config
```

Enter your access token and hit `Enter`.

Configuration done! Let's use:

```
twc --help
```

# Shell completion

## Bash

Add this to **~/.bashrc**:

```
eval "$(_TWC_COMPLETE=bash_source twc)"
```

## Zsh

Add this to **~/.zshrc**:

```
eval "$(_TWC_COMPLETE=zsh_source twc)"
```

## Fish

Add this to **~/.config/fish/completions/tw.fish**:

```
eval (env _TWC_COMPLETE=fish_source twc)
```
