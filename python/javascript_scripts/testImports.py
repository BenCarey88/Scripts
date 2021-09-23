import argparse
import os
import os.path
import re
import sys


# MATCH PATTERNS
# export {object1, object2,...} from 'relative_file_path'
EXPORT_OBJ_FROM = re.compile(
    r"(?<!//)(?P<whole>export\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
)
# export * from 'relative_file_path'
EXPORT_ALL_FROM = re.compile(
    r"(?<!//)(?P<whole>export\s+\*\s+from\s+'(?P<file>[^']+)')"
)
# export <class/var/func/> object
EXPORT_OBJ = re.compile(
    r"(?<!//)(?P<whole>export\s+(?:class|var|function|const|let)?\s+(?P<object>\w+\b))"
)
# import {object1, object2, ...} from 'relative_file_path'
IMPORT_OBJ_FROM = re.compile(
    r"(?<!//)(?P<whole>import\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
)

"""
DATABASE:

dict with the following expected structure:

{
    file_path1: {
        "exports": list(str),
        "recursive_imports": list(set)
        "errors": {
            "export_file_errors": list(str),
            "export_object_errors": list(str),
            "import_file_errors": list(str),
            "import_object_errors": list(str),
            "recursive_imports": list(list(str))
        }
    },
    file_path2: {...},
    ...
}

Keys:
    exports (list(str)): list of js objects exported by this file

    recursive_imports (list(set)): list of sets of files that represent a
        recursive chain of imports called by this file

    errors (dict): dict of errors to be printed to terminal:

        export_file_errors (list(str)): list of nonexistant filepaths appearing
            in export statements in this file
        export_object_errors (list(str)): list of objects appearing in export
            statements in this file that cannot be imported
        import_file_errors (list(str)): list of nonexistant filepaths appearing
            in import statements in this file
        import_object_errors (list(str)): list of objects appearing in import
            statements in this file that cannot be imported
        recursive_imports (list(list(str))): list of lists of files that
            represent a recursive chain of imports called by this file. This
            field will only be filled if the outer recursive_imports key didn't
            already contain this list. This allows us to only print a recursion
            error for one of the files in the chain.
"""
DATABASE = dict()


def search_imports_and_exports(file_path):
    """Search for objects imported/exported by file and add to DATABASE.

    Args:
        file_path (str): path to file.

    Returns:
        (list(str)) all objects exported by file.
    """
    if file_path in DATABASE.keys():
        return DATABASE[file_path]["exports"]

    exports = []
    export_file_errors = []
    export_object_errors = []
    import_file_errors = []
    import_object_errors = []

    DATABASE[file_path] = {
        "exports": exports,
        "errors": {
            "export_file_errors": export_file_errors,
            "export_object_errors": export_object_errors,
            "import_file_errors": import_file_errors,
            "import_object_errors": import_object_errors,
        }
    }

    patterns = [
        EXPORT_OBJ_FROM,
        EXPORT_ALL_FROM,
        EXPORT_OBJ,
        IMPORT_OBJ_FROM,
    ]

    dir_path = os.sep.join(
        file_path.split(os.sep)[:-1]
    )
    with open(file_path, "r") as js_file:
        try:
            contents = js_file.read()
        except:
            print ("\n[WARNING]: could not read ", file_path, "\n")
            return exports

    for pattern in patterns:
        start_pos = 0
        match = pattern.search(contents, start_pos)
        while match:

            if pattern == EXPORT_OBJ_FROM:
                relative_file_path = match.group("file")
                new_file_path = os.path.abspath(
                    os.path.join(dir_path, relative_file_path)
                )
                objects = re.split(
                    r"[,\s]+",
                    match.group("objects"),
                )
                objects = [obj for obj in objects if obj]
                if not os.path.isfile(new_file_path):
                    export_file_errors.append(new_file_path)
                else:
                    for obj in objects:
                        if obj in search_imports_and_exports(new_file_path):
                            exports.append(obj)
                        else:
                            export_object_errors.append(match.group("objects"))

            elif pattern == EXPORT_ALL_FROM:
                relative_file_path = match.group("file")
                new_file_path = os.path.abspath(
                    os.path.join(dir_path, relative_file_path)
                )
                if not os.path.isfile(new_file_path):
                    export_file_errors.append(new_file_path)
                else:
                    exports.extend(
                        search_imports_and_exports(new_file_path)
                    )

            elif pattern == EXPORT_OBJ:
                exports.append(match.group("object"))

            elif pattern == IMPORT_OBJ_FROM:
                relative_file_path = match.group("file")
                new_file_path = os.path.abspath(
                    os.path.join(dir_path, relative_file_path)
                )
                objects = re.split(
                    r"[,\s]+",
                    match.group("objects"),
                )
                objects = [obj for obj in objects if obj]
                if not os.path.isfile(new_file_path):
                    import_file_errors.append(new_file_path)
                else:
                    for obj in objects:
                        if not obj in search_imports_and_exports(new_file_path):
                            import_object_errors.append(obj)

            start_pos = match.end('whole')
            match = pattern.search(contents, start_pos)

    return exports


def test_file_recursion(current_file, start_file, file_list=None, file_list_to_display=None):
    """Check if file imports are recursive and add to DATABASE if they are.
    
    Note this function must be run after search_imports_and_exports, since it
    assumes the DATABASE has already been filled and every file has an entry.

    Args:
        current_file (str): the current_file we're searching.
        start_file (str): the file we first entered this function with, used to
            test against to see if our imports have resulted in a recursive loop.
        file_list (list(str) or None): list of all files we've searched already
            since we first entered this function.
        file_list_to_display (list(str) or None): chain of imports, spanning from
            the file we entered this function with to the current file. If imports
            are recursive, this will be the chain we show in the error message.
            This differs from file_list in that it will only include the offending
            chain, whereas file_list may include additional 'dead-end' files that
            were searched but contained no recursive imports.
    """
    file_list = file_list or []
    file_list_to_display = file_list_to_display or []

    if current_file in file_list:
        if current_file == start_file:
            already_covered_recursions = DATABASE[start_file].get("recursive_imports", [])
            if set(file_list_to_display) not in already_covered_recursions:
                for file in file_list_to_display:
                    # add to list of recursive imports so we don't repeat the same error
                    DATABASE[file].setdefault("recursive_imports", []).append(
                        set(file_list_to_display)
                    )
                DATABASE[start_file]["errors"].setdefault("recursive_imports", []).append(
                    file_list_to_display + [current_file]
                )
        return

    file_list.append(current_file)

    patterns = [
        EXPORT_OBJ_FROM,
        EXPORT_ALL_FROM,
        IMPORT_OBJ_FROM,
    ]

    dir_path = os.sep.join(
        current_file.split(os.sep)[:-1]
    )
    with open(current_file, "r") as js_file:
        try:
            contents = js_file.read()
        except UnicodeDecodeError:
            print ("\n[WARNING]: could not read ", current_file, "\n")
            return

    for pattern in patterns:
        start_pos = 0
        match = pattern.search(contents, start_pos)
        while match:

            relative_file_path = match.group("file")
            new_file_path = os.path.abspath(
                os.path.join(dir_path, relative_file_path)
            )
            if os.path.isfile(new_file_path):
                """Note the distinction:

                With file_list, we mutate the list object, so it contains all
                files we've searched since we first entered the function

                With file_list to display, we create a new variable to pass
                into the function, so it does not contain any dead-end files.
                """
                test_file_recursion(
                    new_file_path,
                    start_file,
                    file_list,
                    file_list_to_display+[current_file],
                )

            start_pos = match.end('whole')
            match = pattern.search(contents, start_pos)


def process_command_line():
    """Setup command line parser and return directory to check.

    Returns:
        (str): absolute path to directory to check for import/export
            errors in.
    """
    parser = argparse.ArgumentParser(
        description="Test relative imports in javascript project."
    )
    parser.add_argument(
        "directory",
        metavar="<directory>",
        default=["."],
        type=str,
        nargs='?', # 0 or 1
        help="path to project directory"
    )
    args = parser.parse_args()

    relative_path_to_proj_dir = next(iter(args.directory), "")
    current_dir = os.getcwd()
    return os.path.abspath(relative_path_to_proj_dir)


def fill_database(directory_path):
    """Fill database with details of errors for directory.
    
    Args:
        directory_path (str): absolute path to directory to check for
            import/export errors in.
    """
    for subdir, dirs, files in os.walk(directory_path):
        for filename in files:
            filepath = os.path.join(subdir, filename)
            if filepath.endswith(".js") or filepath.endswith(".mjs"):
                search_imports_and_exports(filepath)
                test_file_recursion(filepath, filepath)


def get_error_message():
    """Get import and export error messages for DATABASE.

    Returns:
        (str): string to display error messages.
    """
    error_message = "IMPORT/EXPORT ERRORS FOUND:\n\n{0}"
    no_error_message = "NO IMPORT/EXPORT ERRORS FOUND"
    details = ""
    for filename, info in DATABASE.items():
        file_details = ""
        for error_type, error_list in info["errors"].items():
            if error_list:
                message = "\t" + error_type.upper() + "\n\t\t"
                if error_type == "recursive_imports":
                    message += "\n\n\t\t".join(
                        ["\n\t\t".join(sublist) for sublist in error_list]
                    ) 
                else:
                    message += "\n\t\t".join(error_list)
                file_details += message + "\n"
        if file_details:
            details += filename + "\n" + file_details + "\n\n"

    return (
        error_message.format(details) 
        if details
        else no_error_message
    )


if __name__ == "__main__":
    directory = process_command_line()
    fill_database(directory)
    print (get_error_message())
