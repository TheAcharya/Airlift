import argparse
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union

ArgToken = Union[str, Tuple[str, str]]
ArgOption = Dict[str, Any]
ArgSchema = Dict[str, Dict[ArgToken, ArgOption]]
HELP_ARGS_WIDTH = 50

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="airlift",
        description="https://github.com/TheAcharya/csv2notion-neo \n\nUpload csv files to Airtable",
        usage="%(prog)s [-h] --token TOKEN [--url URL] [OPTION]... FILE",
        add_help=False,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=HELP_ARGS_WIDTH
        ),
    )

    schema: ArgSchema = {
        "POSITIONAL":{
            "csv_file":{
                "type":Path,
                "help":"CSV file to upload",
                "metavar":"FILE",
            }
        },
        "general_options":{
            "--token":{
                "help":"You airtable token",
                "required":True,
            },
            "--base":{
                "help":"you base ID",
                "required":True,
            },
            "--table":{
                "help":"your table name",
                "required":True,
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