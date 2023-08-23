# Littlepay

APIs and admin tasks for Littlepay.

## Usage

```console
$ littlepay -h
usage: littlepay [-h] [-v] {config,switch} ...

positional arguments:
  {config,switch}
    config         Get or set configuration.
    switch         Switch the active environment or participant.

options:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
```

## Install

Use `pip` to install from GitHub:

```console
pip install git+https://github.com/cal-itp/littlepay.git@main"
```

## Getting started

If this is your first time using `littlepay`, create a configuration file (using defaults):

```console
littlepay config
```

The location and basic info from your current config file are printed in the terminal:

```
$ littlepay config
Creating config file: /home/calitp/.littlepay/config.yaml
Config: /home/calitp/.littlepay/config.yaml
Envs: prod, qa
Participants: cst
Active: qa, [no participant]
```

### Add configuration

The configuration file is a YAML dictionary tracking `envs` and `participants`:

```yml
active:
  env: qa
  participant: ""
envs:
  prod:
    url: ""
  qa:
    url: ""
participants:
  cst:
    audience: ""
    client_id: ""
    client_secret: ""
```

There are two `envs` by default, the base API URL should be completed for each:

- `qa` is for the testing system
- `prod` is for the live system

Add specifics for the `participants` you manage based on information received from Littlepay support.

### Use a different config file

```console
littlepay config -c /path/to/new/config.yaml
```

The most recent config used is saved for next time.

### Switch the active target

For `envs`:

```console
littlepay switch env <env_name>
```

And `participants`:

```console
littlepay switch participant <participant_id>
```
