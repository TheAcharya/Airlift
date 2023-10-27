<a href="https://github.com/TheAcharya/Airlift"><img src="https://github.com/TheAcharya/Airlift/blob/main/assets/Airlift_Icon.png?raw=true" width="200" alt="App icon" align="left"/>

<div>
<h1>Airlift</h1>
<!-- PyPI -->
<a href="https://pypi.python.org/pypi/csv2notion-neo">
<img src="https://img.shields.io/pypi/v/csv2notion-neo?label=version" alt="PyPI"/>
</a>
<!-- Python -->
<a href="https://pypi.org/project/csv2notion-neo/">
<img src="https://img.shields.io/pypi/pyversions/csv2notion-neo.svg" alt="Python"/>
</a>
<!-- release_github -->
<a href="https://github.com/TheAcharya/Airlift/actions/workflows/release_github.yml">
<img src="https://github.com/TheAcharya/Airlift/actions/workflows/release_github.yml/badge.svg" alt="release_github"/>
</a>
<p>
<p>An express method to upload & merge *.csv or *.json files to <a href="https://notion.so/" target="_blank">Airtable</a>. Airlift uses <a href="https://github.com/gtalarico/pyairtable" target="_blank">pyAirtable</a> API Library.</p>

<br>
<br>
</div>

## Core Features

## Table of contents

- [Background](#background)
- [Installation](#installation)
  - [Pre-compiled Binary (Recommended)](#pre-compiled-binary-recommended)
  - [From Source](#from-source)
- [Guide](#guide)
  - [macOS Gatekeeper & Notarization](#macos-gatekeeper--notarization)
  - [Prerequisite](#prerequisite)
- [Examples](#examples)
- [Credits](#credits)
- [License](#license)
- [Reporting Bugs](#reporting-bugs)

## Background

## Installation

### Pre-compiled Binary (Recommended)

Download the latest release of the latest binary release [here](https://github.com/TheAcharya/airlift/releases).

### With PIP

```bash
$ pip install --user airlift
```

**Python 3.7 or later required.**

### From source

This project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.

```shell
$ git clone https://github.com/TheAcharya/airlift.git
$ cd airlift/
$ poetry install --no-dev
$ poetry run airlift
```

## Guide

```plain
$ airlift --help
usage: airlift [-h] --token TOKEN --base BASE --table TABLE [OPTION]... FILE

https://github.com/TheAcharya/airlift

Upload & Merge Data to Airtable

positional arguments:
  FILE                               CSV file to upload

general options:
  --token TOKEN                      your Airtable personal access token
  --base BASE                        your Airtable Base ID
  --table TABLE                      your Airtable Table ID
  --log FILE                         file to store program log
  --verbose                          output debug information
  --version                          show program's version number and exit
  -h, --help                         show this help message and exit
```

### macOS Gatekeeper & Notarization

After trying to run `airlift` for the first time, the process will be blocked by macOS's Gatekeeper, and a system dialog will appear which includes

> "airlift" can't be opened because the developer cannot be verified...

- To approve the process and allow `airlift` to run, go to System Preferences, Security & Privacy, General, and look in the bottom right corner for a button to click.
- After approving `airlift`, it should run successfully. 
- For more information, visit https://support.apple.com/en-us/HT202491.

### Prerequisite

You must pass a single `*.csv` file for upload. The CSV file must contain at least 2 rows. The first row will be used as a header.

<details><summary>Obtain your Airtable's Personal Access Token:</summary>
<p>

1. Login to your [Airtable](https://airtable.com/login) account via a web browser.
2. Go to [Personal access token](https://airtable.com/create/tokens), click the **Create new token** button to create a new personal access token.
3. Give your token a unique name. This name will be visible in record revision history.
4. Add the following scopes to grant to your token. This controls what API endpoints the token will be able to use.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/airtable_scopes.png?raw=true"> </p>
   
6. Click ‘add a base’ to grant the token access to a base or workspace

> You can grant access to any combination and number of bases and workspaces. You can also grant access to all workspaces and bases under your account. Keep in mind that the token will only be able to read and write data within the bases and workspaces that have been assigned to it.

6. Once your token is created, the token will only be shown to you once, it is encouraged that you to copy it to your clipboard and store it somewhere safe. While you will be able to manage it in [Personal access token](https://airtable.com/create/tokens), the sensitive token itself is not stored for security purposes.

</p>
</details>

<details><summary>Obtain your Airtable's Base ID & Table ID:</summary>
<p>

1. When you have a base open in a compatible web browser, you should see a URL in the address bar that looks similar to the example below:

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/airtable_url.jpg?raw=true"> </p>

In between each backslash, you will find a string that identifies the base, table, and view IDs.

- Base IDs begin with "app"
- Table IDs begin with "tbl"
- View IDs begin with "viw"

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/airtable_url_reference.png?raw=true"> </p>

We only require _Base ID_ and _Table ID_ for **Airlift**

</p>
</details>

## Credits

Original Idea and Workflow Architecture by [Vigneswaran Rajkumar](https://twitter.com/IAmVigneswaran)

Maintained by [Arjun Prakash](https://github.com/arjunprakash027) (1.0.0 ...)

Icon Design by [Bor Jen Goh](https://www.artstation.com/borjengoh)

## License

Licensed under the MIT license. See [LICENSE](https://github.com/TheAcharya/Airlift/blob/main/LICENSE) for details.

## Reporting Bugs

For bug reports, feature requests and other suggestions you can create [a new issue](https://github.com/TheAcharya/Airlift/issues) to discuss.
