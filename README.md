# Cal-ITP Littlepay

Cal-ITP API implementations and admin tasks for Littlepay.

## Usage

```console
$ littlepay -h
usage: littlepay [-h] [-v] [-c CONFIG_PATH] {config,groups,products,switch} ...

positional arguments:
  {config,groups,products,switch}
    config              Get or set configuration
    groups              Interact with groups in the active environment
    products            Interact with products in the active environment
    switch              Switch the active environment or participant

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c CONFIG_PATH, --config CONFIG_PATH
                        Path to a readable and writeable config file to use.
                        File will be created if it does not exist.
```

## Install

Use `pip` to install from GitHub:

```console
pip install git+https://github.com/cal-itp/littlepay.git@main
```

## Getting started

If this is your first time using `littlepay`, create a configuration file (using defaults):

```console
littlepay config
```

The location and basic info from your current config file are printed in the terminal:

```console
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
    qa:
      audience: ""
      client_id: ""
      client_secret: ""
    prod:
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
littlepay config /path/to/new/config.yaml
```

Or

```console
littlepay --config /path/to/new/config.yaml
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

## Work with groups

```console
$ littlepay groups -h
usage: littlepay groups [-h] [-f GROUP_TERMS] [--csv] {create,funding_sources,link,migrate,products,remove,unlink} ...

positional arguments:
  {create,funding_sources,link,migrate,products,remove,unlink}
    create              Create a new concession group
    funding_sources     List funding sources for one or more concession groups
    link                Link one or more concession groups to a product
    migrate             Migrate a group from the old Customer Group format to the current format
    products            List products for one or more concession groups
    remove              Remove an existing concession group
    unlink              Unlink a product from one or more concession groups

options:
  -h, --help            show this help message and exit
  -f GROUP_TERMS, --filter GROUP_TERMS
                        Filter for groups with matching group ID or label
  --csv                 Output results in simple CSV format
```

### List existing groups

Print all groups in the active environment:

```console
littlepay groups
```

Filter for groups with a matching ID or label:

```console
littlepay groups -f <term>
```

Multiple filters are OR'd together:

```console
littlepay groups -f <term1> -f <term2>
```

### Create a new group

```console
littlepay groups create <label>
```

### Delete an existing group

With confirmation:

```console
littlepay groups remove <group_id>
```

Without confirmation:

```console
littlepay groups remove --force <group_id>
```

## Work with products

```console
$ littlepay products -h
usage: littlepay products [-h] [-f PRODUCT_TERMS] [-s {ACTIVE,INACTIVE,EXPIRED}] [--csv] {link,unlink} ...

positional arguments:
  {link,unlink}
    link                Link one or more products to a concession group
    unlink              Unlink a concession group from one or more products

options:
  -h, --help            show this help message and exit
  -f PRODUCT_TERMS, --filter PRODUCT_TERMS
                        Filter for products with matching product ID, code, or description
  -s {ACTIVE,INACTIVE,EXPIRED}, --status {ACTIVE,INACTIVE,EXPIRED}
                        Filter for products with matching status
  --csv                 Output results in simple CSV format
```

### List existing products

```console
littlepay products
```

Filtering works the same as for groups, matching against product ID, code, or description:

```console
littlepay products -f <term>
```

```console
littlepay products -f <term1> -f <term2>
```

Also supports filtering by status (`ACTIVE`, `INACTIVE`, `EXPIRED`):

```console
littlepay products -s EXPIRED
```

```console
littlepay products -f <term> -s ACTIVE
```

### List linked products for one or more groups

For each group, output the group's linked products. Builds on the filtering sytax.

E.g. to list linked products for all groups:

```console
littlepay groups products
```

Or to list linked products for a specific group:

```console
littlepay groups -f <group_id> products
```

### Link and unlink a product to one or more groups

For each group, link the given product to the group. Builds on the filtering syntax.

E.g. to link a product to all groups:

```console
littlepay groups link <product_id>
```

Or to link a product to a specific group:

```console
littlepay groups -f <group_id> link <product_id>
```

Unlinking groups from a product works the same:

```console
littlepay groups -f <group_id> unlink <product_id>
```

### Link and unlink a group to one or more products

For each product, link the given group to the product. Builds on the filtering syntax.

E.g. to link a group to all products:

```console
littlepay products link <group_id>
```

Or to link a group to a specific product:

```console
littlepay products -f <product_id> link <group_id>
```

Unlinking products from a group works the same:

```console
littlepay products -f <product_id> unlink <group_id>
```

## Version and release

The package version is derived from git metadata via [`setuptools_scm`](https://setuptools-scm.readthedocs.io/en/latest/).

Pushing a tag with the correct format generates a new GitHub release, which can then be finalized and published.

### Release a new version

1. Ensure you are on the latest commit of `main`:

   ```bash
   git checkout main
   git pull
   ```

1. Create an [_annotated_](https://git-scm.com/book/en/v2/Git-Basics-Tagging#_annotated_tags), [Calver-formatted](https://calver.org/) tag based on the release year, month, and sequence counter:

   ```bash
   git tag -a YYYY.MM.N
   ```

   You may also create a _release candidate_, by appending `-rcX` where `X` is the release candidate sequence counter:

   ```bash
   git tag -a YYYY.MM.N-rcX
   ```

   In either case, provide a short comment for the tag.

1. Push the tag to GitHub:

   ```bash
   git push origin YYYY.MM.N
   ```

1. Observe the [Release workflow](https://github.com/cal-itp/littlepay/actions/workflows/release.yml)
