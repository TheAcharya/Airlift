<a href="https://github.com/TheAcharya/Airlift"><img src="https://github.com/TheAcharya/Airlift/blob/main/assets/Airlift_Icon.png?raw=true" width="200" alt="App icon" align="left"/>

<div>
<h1>Airlift</h1>
<!-- PyPI -->
<a href="https://pypi.python.org/pypi/airlift_py">
<img src="https://img.shields.io/pypi/v/airlift_py?label=version" alt="PyPI"/>
</a>
<!-- Python -->
<a href="https://pypi.org/project/airlift_py/">
<img src="https://img.shields.io/pypi/pyversions/airlift_py.svg" alt="Python"/>
</a>
<!-- release_github -->
<a href="https://github.com/TheAcharya/Airlift/actions/workflows/release_github.yml">
<img src="https://github.com/TheAcharya/Airlift/actions/workflows/release_github.yml/badge.svg" alt="release_github"/>
</a>
<p>
<p>An automated method to upload & merge *.csv or *.json data files with attachments to <a href="https://www.airtable.com" target="_blank">Airtable</a> database.</p>

<br>
<br>
</div>

## Core Features

- Automated uploading of `.csv` or `.json` data to Airtable
- Ability to update and auto-create new entries for [single select field](https://support.airtable.com/docs/single-select-field) and [multiple select field](https://support.airtable.com/docs/multiple-select-field)
- No subscription of third party platform required
- Ability to upload attachments via build-in Dropbox client
- Ability to upload attachments to multiple attachment columns
- Uses long-lived refresh token for Dropbox client

## Table of contents

- [Background](#background)
- [Installation](#installation)
  - [Pre-compiled Binary (Recommended)](#pre-compiled-binary-recommended)
  - [From Source](#from-source)
- [Guide](#guide)
  - [macOS Gatekeeper & Notarization](#macos-gatekeeper--notarization)
- [Prerequisite](#prerequisite)
  - [Airtable](#airtable)
  - [Dropbox](#dropbox)
- [Column Types](#column-types)
- [Examples](#examples)
- [Future Roadmap](#future-roadmap)
- [Credits](#credits)
- [License](#license)
- [Reporting Bugs](#reporting-bugs)

## Background

**Airlift** draws inspiration from our very own [CSV2Notion Neo](https://github.com/TheAcharya/csv2notion-neo), which was inspired by Airtable’s [CSV import extension](https://support.airtable.com/docs/csv-import-extension). And with **Airlift**, we have come full circle.

To send data to Airtable, users or applications need to write custom code using libraries that connect with Airtable's API. For normal end-users who aren’t developers, this can be an extremely challenging endeavor. For most users, Airtable’s [CSV import extension](https://support.airtable.com/docs/csv-import-extension) could be sufficient. But [CSV import extension](https://support.airtable.com/docs/csv-import-extension) is only available on paid plan.

Furthermore, many experienced Airtable users want to send and transfer data automatically without using [Make](https://www.make.com) or [Zapier](https://zapier.com). This is where **Airlift** comes into play.

**Airlift** is free and open-source software. But you can [sponsor](https://github.com/sponsors/TheAcharya) us if you find it useful.

## Installation

### Pre-compiled Binary (Recommended)

Download the latest release of the latest binary release [here](https://github.com/TheAcharya/airlift/releases).

### With PIP

```bash
$ pip install --user airlift-py
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

Upload & Merge Data with Attachments to Airtable

positional arguments:
  FILE                               CSV or JSON file to upload

general options:
  --token TOKEN                      your Airtable personal access token
  --base BASE                        your Airtable Base ID
  --table TABLE                      your Airtable Table ID
  --log FILE                         file to store program log
  --verbose                          output debug information
  --version                          show program's version number and exit
  --workers                          total number of worker threads to upload your data (default: 5)
  -h, --help                         show this help message and exit

dropbox options:
  --dropbox-token FILE               your JSON file with Dropbox API App key
  --dropbox-refresh-token            switch to change your refresh token
  --attachment-columns               specify one or more attachment columns
  --attachment-columns-map           specify how the attachment column must be mapped in Airtable

column options:
  --disable-bypass-column-creation   creates new columns that are not present in Airtable's table

validation options:
  --fail-on-duplicate-csv-columns    fail if CSV has duplicate columns;
                                     otherwise last column will be used
```

### macOS Gatekeeper & Notarization

After trying to run `airlift` for the first time, the process will be blocked by macOS's Gatekeeper, and a system dialog will appear which includes

> "airlift" can't be opened because the developer cannot be verified...

- To approve the process and allow `airlift` to run, go to System Preferences, Security & Privacy, General, and look in the bottom right corner for a button to click.
- After approving `airlift`, it should run successfully. 
- For more information, visit https://support.apple.com/en-us/HT202491.

## Prerequisite

### Airtable

You must pass a single `*.csv` or `*.json` file for upload. The CSV file must contain at least 2 rows. The first row will be used as a header.

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

Airtable's API does not allow direct uploading of attachments. In order to upload an attachment via Airtable's API, the attachment must first exist at a publicly accessible url. To mitigate this problem, Airlift will utilise [Dropbox](https://www.dropbox.com) as a temporary storage provider. [Dropbox’s basic account](https://www.dropbox.com/basic) offers 2GB of free storage. We believe it would be adequate for most operations.

### Dropbox

<details><summary>Obtain your Dropbox App Key and Authorisation code:</summary>
<p>

1. Right-click and save [dropbox-token.json](https://raw.githubusercontent.com/TheAcharya/Airlift/main/assets/dropbox-token.json) file to your computer.
2. When using `--dropbox-token` make sure you input the full `PATH` of `dropbox-token.json` file.
3. Login to your [Dropbox's App Console](https://www.dropbox.com/developers/apps) account via a web browser.
4. Click on ‘Create app’ button.
5. Choose Scoped access.
6. Choose Full Dropbox access.
7. Give your App a name. _The name of the App can be unique and personal to you._
8. Click on ‘Create app’ button.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_01.png?raw=true"> </p>

7. Go to the Permissions tab.
8. Set the permissions as shown on the screenshot.
9. Click on 'Submit' at the bottom.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_02.png?raw=true"> </p>

10. Go to the Settings tab.
11. Copy your App key and paste into your `dropbox-token.json` file. Where `REPLACE` is your App key.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_03.png?raw=true"> </p>

```json
{
  "app_key": "REPLACE"
}
```

12. On first usage of Airlift, you will be promted to visit Dropbox.
13. Copy and paste the full Dropbox URL into your browser.

```txt
INFO: Validation done!
INFO: All the columns are verified and present in both the file and Airtable!
1. Go to: https://www.dropbox.com/oauth2/authorize?response_type=code&client_id=6zh18qgnw37ifpp&token_access_type=offline&code_challenge=TphrwcwmRtkGawgxFvWQcROFMbjsTeba9BGv0Lgi0nw&code_challenge_method=S256
2. Click "Allow" (you might have to log in first).
3. Copy the authorization code.
Enter the authorization code here:    
```

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_04.png?raw=true"> </p>

14. Click Continue.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_04.png?raw=true"> </p>

15. Click Allow.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_05.png?raw=true"> </p>

16. You will be presented with your authorization code. Copy your authorization code.

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/dropbox_06.png?raw=true"> </p>

```bash
Enter the authorization code here:    XXXZZaa0-poAAAAAAABZNgc9CwNdyryqoRAi4fxP2aU
```

17. Paste it back into the terminal.
18. Airlift would update and store your Dropbox refresh token into your `dropbox-token.json` file.
19. This is a one time procress. You will not be asked again.

**Do not share your access json token file with anyone.**

</p>
</details>

<details><summary>Reset and Update your Dropbox App key:</summary>
<p>

1. For reasons should you decide to delete and revoke the App from [Dropbox's App Console](https://www.dropbox.com/developers/apps) and created a new App, you would have to repeate the above mentioned steps.
2. For easy updating of your your Dropbox App key, right-click and save [reset-create-dropbox-app-key.sh](https://raw.githubusercontent.com/TheAcharya/Airlift/main/assets/reset-create-dropbox-app-key.sh) file to the same location of your `dropbox-token.json` file.
4. To execute your script, open Terminal, type `sh ` and drag and drop `reset-create-dropbox-app-key.sh` file into the terminal.
5. You will promted to enter your Dropbox App key.
6. The script would overwrite `dropbox-token.json` file with your new Dropbox App key.

</p>
</details>

<details><summary>Creating your Dropbox refresh token:</summary>
<p>

If you have created your and replaced your Dropbox App key in your `dropbox-token.json` file. You would need to re-create your Dropbox refresh token again.

You can utalise this this `.sh` shoukd you need to authorise and refresh your `dropbox-token.json` file.

```bash
#!/bin/sh

TOOL_PATH="/Users/xxx/Desktop/Airlift/airlift"
DROPBOX_TOKEN="/Users/xxx/Desktop/Airlift/dropbox-token.json"
UPLOAD_LOG="/Users/xxx/Desktop/Airlift/log.txt"

$TOOL_PATH --dropbox-token $DROPBOX_TOKEN --dropbox-refresh-token --log $UPLOAD_LOG
```

</p>
</details>

## Column Types

By default, Airlift will try to guess column types based on their content.

Some column types do not support assigning value to them because the database generates their content automatically.

<details><summary>Support Table</summary>
<p>

| Column Type Name   | Supported Values | Multiple Values (Comma Separated) |
| ----------------------- | ---------------- | -------------------------------------- |
| Attachment              | string           | ❌                                     |
| Autonumber              | numerical        | ❌                                     |
| Barcode                 | string           | ❌                                     |
| Button                  | `---`            | `---`                                  |
| Checkbox                | `true`, `false`  | ❌                                     |
| Count                   | numerical        | ❌                                     |
| Created time            | `---`		         | `---`                                  |
| Created by              | `---`  		       | `---`                                  |
| Currency                | numerical        | ❌                                     |
| Date & Time             | string  		     | ❌                                     |
| Duration                | string           | ❌                                     |
| Email                   | string           | ❌                                     |
| Formula                 | `---`            | `---`                                  |
| Last modified by        | `---`            | `---`                                  |
| Last modified time      | `---`            | `---`                                  |
| Linked record           | string           | ✅                                     |
| Long text           	  | string           | ❌                                     |
| Lookup                  | `---`            | `---`                                  |
| Multiple select         | string           | ✅                                     |
| Number       			      | numerical        | ❌                                     |
| Percent                 | numerical        | ❌                                     |
| Phone number            | string           | ❌                                     |
| Rating                  | numerical        | ❌                                     |
| Rollup                  | `---`            | `---`                                  |
| Single line text        | string           | ❌                                     |
| Single select        	  | string           | ❌                                     |
| URL       			        | string           | ❌                                     |
| User       			        | `---`            | `---`                                  |

</p>
</details>

## Examples

<details><summary>Basic creation of folders and .sh file</summary>
<p>

For ease of use, usage and creation of `.sh` files is **recommended**.

1. Create a folder called **Airlift** on your Desktop.
2. Place the latest pre-compiled binary with the folder.
3. Right-click and save [dropbox-token.json](https://raw.githubusercontent.com/TheAcharya/Airlift/main/assets/dropbox-token.json) file and save it within your **Airlift**. 
4. Within that folder, create a folder, **Data**.
5. **Data** is where you place your `.csv` or `.json` and attachments files.
6. Create a file using any text editor. Name the script file with extension `.sh`
7. Copy and paste this syntax into the file, where **xxx** is the name of of your user directory and **zzz** is the name of your `.csv` or `.json` file.
8. **REPLACE** the text with your relevent tokens and IDs.
9. Save the script file as `myscript.sh` within your **Airlift** folder.
10. To give execute permission to your script, open Terminal, `chmod +x /Users/xxx/Desktop/Airlift/myscript.sh`
12. To execute your script, open Terminal, `sh /Users/xxx/Desktop/Airlift/myscript.sh`
13. To obtain your Dropbox App Key and Authorization code, please read the [Dropbox](#dropbox) section.
14. You can create and save multiple `.sh` files for different modes and configurations.

</p>
</details>

<details><summary>Uploading Data without Attachments</summary>
<p>

```bash
#!/bin/sh

TOOL_PATH="/Users/xxx/Desktop/Airlift/airlift"
AIRTABLE_TOKEN="REPLACE"
AIRTABLE_BASE="REPLACE"
AIRTABLE_TABLE="REPLACE"
UPLOAD_PAYLOAD="/Users/xxx/Desktop/Airlift/Data/zzz.csv"
UPLOAD_LOG="/Users/xxx/Desktop/Airlift/log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --log $UPLOAD_LOG "$UPLOAD_PAYLOAD"
```

Example CSV

```text
Cat ID,Animal Name,Location
001,Lion,Namibia
002,Tiger,India
003,Panther,India
004,Snow Leopard,Nepal
005,Cheetah,South Africa
006,Puma,South America
007,Jaguar,Brazil
```

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/big-cats-without-attachments.gif?raw=true"> </p>

</p>
</details>

<details><summary>Uploading Data with Attachments</summary>
<p>

```bash
#!/bin/sh

TOOL_PATH="/Users/xxx/Desktop/Airlift/airlift"
AIRTABLE_TOKEN="REPLACE"
AIRTABLE_BASE="REPLACE"
AIRTABLE_TABLE="REPLACE"
DROPBOX_TOKEN="/Users/xxx/Desktop/Airlift/dropbox-token.json"
UPLOAD_PAYLOAD="/Users/xxx/Desktop/Airlift/Data/zzz.csv"
UPLOAD_LOG="/Users/xxx/Desktop/Airlift/log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --dropbox-token $DROPBOX_TOKEN --attachment-columns "Image Filename" --log $UPLOAD_LOG "$UPLOAD_PAYLOAD"
```

Example CSV 

```text
Cat ID,Animal Name,Location,Image Filename
001,Lion,Namibia,lion.jpg
002,Tiger,India,tiger.jpg
003,Panther,India,panther.jpg
004,Snow Leopard,Nepal,snow_leopard.jpg
005,Cheetah,South Africa,cheetah.jpg
006,Puma,South America,puma.jpg
007,Jaguar,Brazil,jaguar.jpg
```

Example Folder Structure

```text
Desktop/
├─ Airlift/
│  ├─ Data/
│  │  ├─ zzz.csv
│  │  ├─ cheetah.jpg
│  │  ├─ jaguar.jpg
│  │  ├─ lion.jpg
│  │  ├─ panther.jpg
│  │  ├─ puma.jpg
│  │  ├─ snow_leopard.jpg
│  │  ├─ tiger.jpg
│  ├─ myscript.sh
│  ├─ dropbox-token.json
│  ├─ airlift [Binary Executable File]
```

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/big-cats-with-attachments.gif?raw=true"> </p>

</p>
</details>

<details><summary>Uploading Data with Multiple Attachments Column</summary>
<p>

```bash
#!/bin/sh

TOOL_PATH="/Users/xxx/Desktop/Airlift/airlift"
AIRTABLE_TOKEN="REPLACE"
AIRTABLE_BASE="REPLACE"
AIRTABLE_TABLE="REPLACE"
DROPBOX_TOKEN="/Users/xxx/Desktop/Airlift/dropbox-token.json"
UPLOAD_PAYLOAD="/Users/xxx/Desktop/Airlift/Data/zzz.csv"
UPLOAD_LOG="/Users/xxx/Desktop/Airlift/log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --dropbox-token $DROPBOX_TOKEN --attachment-columns "Colour Image" "Black & White Image" --log $UPLOAD_LOG "$UPLOAD_PAYLOAD"
```

Example CSV 

```text
Cat ID,Animal Name,Location,Colour Image,Black & White Image
001,Lion,Namibia,Colour/lion.jpg,Black & White/lion.jpg
002,Tiger,India,Colour/tiger.jpg,Black & White/tiger.jpg
003,Panther,India,Colour/panther.jpg,Black & White/panther.jpg
004,Snow Leopard,Nepal,Colour/snow_leopard.jpg,Black & White/snow_leopard.jpg
005,Cheetah,South Africa,Colour/cheetah.jpg,Black & White/cheetah.jpg
006,Puma,South America,Colour/puma.jpg,Black & White/puma.jpg
007,Jaguar,Brazil,Colour/jaguar.jpg,Black & White/jaguar.jpg
```

Example Folder Structure

```text
Desktop/
├─ Airlift/
│  ├─ Data/
│  │  ├─ zzz.csv
│  │  ├─ Black & White/
│  │  │  ├─ cheetah.jpg
│  │  │  ├─ jaguar.jpg
│  │  │  ├─ lion.jpg
│  │  │  ├─ panther.jpg
│  │  │  ├─ puma.jpg
│  │  │  ├─ snow_leopard.jpg
│  │  │  ├─ tiger.jpg
│  │  ├─ Colour/
│  │  │  ├─ cheetah.jpg
│  │  │  ├─ jaguar.jpg
│  │  │  ├─ lion.jpg
│  │  │  ├─ panther.jpg
│  │  │  ├─ puma.jpg
│  │  │  ├─ snow_leopard.jpg
│  │  │  ├─ tiger.jpg
│  ├─ myscript.sh
│  ├─ dropbox-token.json
│  ├─ airlift [Binary Executable File]
```

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/big-cats-with-attachments-multi-column.gif?raw=true"> </p>

</p>
</details>

<details><summary>Uploading Data with Attachments using Mapping</summary>
<p>

```bash
#!/bin/sh

TOOL_PATH="/Users/xxx/Desktop/Airlift/airlift"
AIRTABLE_TOKEN="REPLACE"
AIRTABLE_BASE="REPLACE"
AIRTABLE_TABLE="REPLACE"
DROPBOX_TOKEN="/Users/xxx/Desktop/Airlift/dropbox-token.json"
UPLOAD_PAYLOAD="/Users/xxx/Desktop/Airlift/Data/zzz.csv"
UPLOAD_LOG="/Users/xxx/Desktop/Airlift/log.txt"

$TOOL_PATH --token $AIRTABLE_TOKEN --base $AIRTABLE_BASE --table $AIRTABLE_TABLE --dropbox-token $DROPBOX_TOKEN --attachment-columns-map "Image Filename" "Attachments" --log $UPLOAD_LOG "$UPLOAD_PAYLOAD"
```

Example CSV 

```text
Cat ID,Animal Name,Location,Image Filename
001,Lion,Namibia,lion.jpg
002,Tiger,India,tiger.jpg
003,Panther,India,panther.jpg
004,Snow Leopard,Nepal,snow_leopard.jpg
005,Cheetah,South Africa,cheetah.jpg
006,Puma,South America,puma.jpg
007,Jaguar,Brazil,jaguar.jpg
```

Example Folder Structure

```text
Desktop/
├─ Airlift/
│  ├─ Data/
│  │  ├─ zzz.csv
│  │  ├─ cheetah.jpg
│  │  ├─ jaguar.jpg
│  │  ├─ lion.jpg
│  │  ├─ panther.jpg
│  │  ├─ puma.jpg
│  │  ├─ snow_leopard.jpg
│  │  ├─ tiger.jpg
│  ├─ myscript.sh
│  ├─ dropbox-token.json
│  ├─ airlift [Binary Executable File]
```

<p align="center"> <img src="https://github.com/TheAcharya/Airlift/blob/main/assets/big-cats-with-attachments-map.gif?raw=true"> </p>

</p>
</details>

## Future Roadmap

- Funtion to create new Airtable Bases
- Funtion to Update & Add New Unique Records
- Robust Validation Options
- And many more...

## Credits

Original Idea and Workflow Architecture by [Vigneswaran Rajkumar](https://twitter.com/IAmVigneswaran)

Maintained by [Arjun Prakash](https://github.com/arjunprakash027) (1.0.0 ...)

Icon Design by [Bor Jen Goh](https://www.artstation.com/borjengoh)

## License

Licensed under the MIT license. See [LICENSE](https://github.com/TheAcharya/Airlift/blob/main/LICENSE) for details.

## Reporting Bugs

For bug reports, feature requests and other suggestions you can create [a new issue](https://github.com/TheAcharya/Airlift/issues) to discuss.
