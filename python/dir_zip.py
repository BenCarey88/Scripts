"""Command line script to zip and unzip directories to/from json files."""

import argparse
import json
import os
import shutil
import sys


def get_args():
    """Parse commandline args.

    The commandline interface uses two subcommands, zip and unzip.

    Returns:
        (argparse.Namespace): commandline arguments.
    """
    parser = argparse.ArgumentParser(
        description='compress directory to json file, or vice versa.'
    )
    command = parser.add_subparsers(dest='command')
    zip_command = command.add_parser(
        "zip",
        help="zip directory into json file",
    )
    unzip_command = command.add_parser(
        "unzip",
        help="unzip json file into directory"
    )

    zip_command.add_argument(
        "directory",
        nargs=1,
        type=str,
        help="path to directory to zip",
    )
    zip_command.add_argument(
        "json",
        nargs=1,
        type=str,
        help="path to json file to zip to",
    )
    zip_command.add_argument(
        "-f",
        action="store_true",
        help="force write (don't ask for confirmation if overwriting)",
    )
    zip_command.add_argument(
        "-g",
        action="store_true",
        help="include git files",
    )

    unzip_command.add_argument(
        "json",
        nargs=1,
        type=str,
        help="path to json file to unzip",
    )
    unzip_command.add_argument(
        "directory",
        nargs=1,
        type=str,
        help="path to directory to save unzipped files to",
    )
    unzip_command.add_argument(
        "-f",
        action="store_true",
        help="force write (don't ask for confirmation if overwriting)",
    )

    return parser.parse_args()


def add_files_to_dict(directory, directory_dict, include_git=False):
    """Recursively add text from files in a directory to a dict.

    Args:
        directory (str): directory to look for files and subdirs in.
        directory_dict (dict): dictionary to store the file text and
            subdirectory dicts in.
        include_git (bool): if False, ignore all git files in directory.
    """
    for file_or_dir in os.listdir(directory):
        if not include_git and file_or_dir.startswith(".git"):
            continue
        file_or_dir_path = os.path.join(directory, file_or_dir)
        if os.path.isfile(file_or_dir_path):
            with open(file_or_dir_path, "r") as file_:
                text = file_.read()
            try:
                text.decode("utf-8")
            except:
                # if can't be utf-decoded then can't be json-ified
                continue
            directory_dict[file_or_dir] = text
        elif os.path.isdir(file_or_dir_path):
            subdir_dict = {}
            directory_dict[file_or_dir] = subdir_dict
            add_files_to_dict(file_or_dir_path, subdir_dict)


def write_files_from_dict(directory, directory_dict):
    """Recursively write files and subdirectories from dict representation.

    Args:
        directory (str): directory to write files to.
        directory_dict (dict): dictionary that defines the files and subdirs.
    """
    os.mkdir(directory)
    for file_or_dir, text_or_subdict in directory_dict.items():
        file_or_dir_path = os.path.join(directory, file_or_dir)
        string_types = (str)
        if sys.version_info[0] < 3:
            string_types = (str, unicode)
        if isinstance(text_or_subdict, string_types):
            with open(file_or_dir_path, "w+") as file_:
                try:
                    file_.write(text_or_subdict)
                except:
                    # just ignore files that we can't decode
                    continue
        elif isinstance(text_or_subdict, dict):
            write_files_from_dict(file_or_dir_path, text_or_subdict)


if __name__ == "__main__":
    """Run commandline interface."""

    args = get_args()
    directory = os.path.join(args.directory[0])
    json_file = os.path.join(args.json[0])
    force = args.f

    # zip
    if args.command == "zip":
        json_file_dir = os.path.dirname(json_file)
        if not os.path.isdir(json_file_dir):
            raise Exception(
                "json file directory {0} does not exist".format(json_file_dir)
            )
        if not os.path.isdir(directory):
            raise Exception(
                "directory {0} doesn't exist".format(directory)
            )
        if not force and os.path.isfile(json_file):
            raise Exception(
                "json file {0} already exists".format(json_file)
            )

        file_dict = {}
        add_files_to_dict(directory, file_dict, args.g)
        with open(json_file, "w+") as file_:
            json.dump(file_dict, file_, indent=4)

    # unzip
    if args.command == "unzip":
        directory_dir = os.path.dirname(directory)
        if not os.path.isdir(directory_dir):
            raise Exception(
                "parent directory {0} does not exist".format(directory_dir)
            )
        if not os.path.isfile(json_file):
            raise Exception(
                "json file {0} doesn't exist".format(json_file)
            )
        if os.path.isdir(directory):
            if not force:
                raise Exception(
                    "directory {0} already exists".format(directory)
                )
            else:
                shutil.rmtree(directory)

        with open(json_file, "r") as file_:
            file_dict = json.load(file_)
        write_files_from_dict(directory, file_dict)
