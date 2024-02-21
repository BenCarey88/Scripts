"""Script to convert .mjs javascript files to .js files."""

import argparse
import os


def process_command_line():
    """Setup command line parser and return directory to check.

    Returns:
        (argparse.Namespace): arguments from commandline.
    """
    parser = argparse.ArgumentParser(
        description="Test relative imports in javascript project."
    )
    parser.add_argument(
        "directory",
        metavar="<directory>",
        default=".",
        type=str,
        nargs='?', # 0 or 1
        help="path to project directory"
    )
    return parser.parse_args()


if __name__ == "__main__":
    directory = process_command_line().directory
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(subdir, filename)
            if filepath.endswith(".js"):
                new_filepath = os.path.join(
                    subdir,
                    filename.rstrip("js") + "mjs"
                )
                print ("Renaming ", filepath, " to ", new_filepath, "\n\n")
                os.rename(filepath, new_filepath)
