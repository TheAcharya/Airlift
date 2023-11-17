import argparse
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
from airlift_py.version import __version__

ArgToken = Union[str, Tuple[str, str]]
ArgOption = Dict[str, Any]
ArgSchema = Dict[str, Dict[ArgToken, ArgOption]]
HELP_ARGS_WIDTH = 50

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="airlift",
        description="https://github.com/TheAcharya/Airlift \n\nUpload & Merge Data with Attachments to Airtable",
        usage="%(prog)s [-h] --token TOKEN --base BASE --table TABLE [OPTION]... FILE",
        add_help=False,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=HELP_ARGS_WIDTH
        ),
    )

    schema: ArgSchema = {
        "POSITIONAL": {
            "csv_file": {
                "type": Path,
                "help": "CSV or JSON file to upload",
                "metavar": "FILE",
                "nargs":"?",
            }
        },
        "general_options": {
            "--token": {
                "help": "your Airtable personal access token",
                
            },
            "--base": {
                "help": "your Airtable Base ID",
            
            },
            "--table": {
                "help": "your Airtable Table ID",
            
            },
            "--log": {
                "type": Path,
                "metavar": "FILE",
                "help": "file to store program log",
            },
            "--verbose": {
                "action": "store_true",
                "help": "output debug information",
            },
            "--version": {
                "action": "version",
                "version": f"%(prog)s {__version__}",
            },
            "--workers": {
                "type": int,
                "help": "total number of worker threads to upload your data (default: 5)"
            },
            ("-h", "--help"): {
                "action": "help",
                "help": "show this help message and exit",
            },
        },
        "dropbox options": {
            "--dropbox-token": {
                "type":Path,
                "help": "your JSON file with Dropbox API App key",
                "metavar":'FILE',
            },
            "--dropbox-refresh-token":{
                "action":"store_true",
                "help":"switch to change your refresh token",
            },
            "--attachment-columns": {
                "nargs": "+",
                "help": "specify one or more attachment columns",
                "metavar":"\b",
            },
            "--attachment-columns-map":{
                "nargs":2,
                "help":"specify how the attachment column must be mapped in Airtable",
                "metavar":"\b",
            },
        },
        "column_options": {
            "--disable-bypass-column-creation": {
                "action": "store_true",
                "help": "creates new columns that are not present in Airtable's table",
            },
        },
        "custom application options": {
            "--md": {
                "action": "store_true",
                "help": argparse.SUPPRESS,
            },
        },
        "validation_options": {
            "--fail-on-duplicate-csv-columns": {
                "action": "store_true",
                "help": (
                    "fail if CSV has duplicate columns"
                    "\notherwise first column will be used"
                ),
            },
        },
    }

    _parse_schema(parser, schema)
    return parser.parse_args(argv)

def _parse_schema(
        parser: argparse.ArgumentParser, schema: ArgSchema
) -> None:
    group: argparse._ActionsContainer

    for group_name, group_args in schema.items():

        if group_name == "POSITIONAL":
            group = parser
        else:
            group = parser.add_argument_group(group_name)

        for arg, arg_params in group_args.items():
            opt_arg = [arg] if isinstance(arg, str) else arg
            group.add_argument(*opt_arg, **arg_params)
