<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://ec650031-twc-cli.s3.timeweb.cloud/dark.svg" type="image/svg+xml">
  <source media="(prefers-color-scheme: dark)" srcset="https://ec650031-twc-cli.s3.timeweb.cloud/dark.png" type="image/png">
  <source media="(prefers-color-scheme: light)" srcset="https://ec650031-twc-cli.s3.timeweb.cloud/light.svg" type="image/svg+xml">
  <source media="(prefers-color-scheme: light)" srcset="https://ec650031-twc-cli.s3.timeweb.cloud/light.png" type="image/png">
  <img alt="TWC CLI" src="https://ec650031-twc-cli.s3.timeweb.cloud/light.png">
</picture>

Timeweb Cloud Command Line Interface and simple SDK 💫

> [Руководство пользователя](https://github.com/timeweb-cloud/twc/blob/master/docs/ru/README.md) 🇷🇺  
> [Command Line Interface (CLI) Reference](https://github.com/timeweb-cloud/twc/blob/master/docs/ru/CLI_REFERENCE.md) 📜

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

To install completion script run:

```
twc --install-completion
```

**twc** automatically detect your shell. Supported: Bash, Zsh, Fish, PowerShell.

