<a href="https://github.com/TheAcharya/csv2notion-neo"><img src="https://github.com/TheAcharya/csv2notion-neo/blob/master/assets/CSV2Notion Neo_Icon.png?raw=true" width="200" alt="App icon" align="left"/>

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
usage: airlift [-h] --token TOKEN [--url URL] [OPTION]... FILE

https://github.com/TheAcharya/airlift

Upload & Merge Data to Airtable

positional arguments:
  FILE                               CSV file to upload

general options:
  --token TOKEN                      Notion token, stored in token_v2 cookie for notion.so
  --url URL                          Notion database URL; if none is provided, will create a new database
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

## Credits

Original Idea and Workflow by [Vigneswaran Rajkumar](https://twitter.com/IAmVigneswaran)

Maintained by [Arjun Prakash](https://github.com/arjunprakash027) (1.0.0 ...)

Icon Design by [Bor Jen Goh](https://www.artstation.com/borjengoh)

## License

Licensed under the MIT license. See [LICENSE](https://github.com/TheAcharya/Airlift/blob/main/LICENSE) for details.

## Reporting Bugs

For bug reports, feature requests and other suggestions you can create [a new issue](https://github.com/TheAcharya/Airlift/issues) to discuss.
