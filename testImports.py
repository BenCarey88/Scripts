import argparse
import os
import os.path
import re
import sys


DATABASE = dict()


parser = argparse.ArgumentParser(
    description="Test relative imports in javascript project."
)

parser.add_argument(
    "-d",
    metavar="<directory>",
    default=[""],
    type=str,
    nargs=1,
    help="path to project directory"
)


# make patterns globals
def search_imports_and_exports(current_file, start_file, file_list=[], file_list_to_display=[]): #file_path, file_list=[], check_recursive=False):
    """Search for objects imported/exported by file and add to DATABASE.

    Args:
        file_path (str): path to file.
        file_list (list(str)): list of filepaths, to check if we end up
            revisiting the same file (hence have recursive imports)

    Returns:
        (list(str)) all objects exported by file.
    """
    file_path = current_file

    if current_file in file_list:
        #file_list.append(current_file)
        if current_file == start_file:
            #print len(file_list)
            #print " "
            #print "\n".join(file_list_to_display + [current_file])
            DATABASE[start_file]["recursive_imports"] = file_list_to_display + [current_file]
            #error_found = Truefcd
        return DATABASE[file_path]["exports"]
    file_list.append(current_file)

    #file_list.append(file_path)

    if file_path in DATABASE.keys():
        return DATABASE[file_path]["exports"]

    exports = []
    export_file_errors = []
    export_object_errors = []
    import_file_errors = []
    import_object_errors = []
    
    DATABASE[file_path] = {
        "exports": exports,
        "export_file_errors": export_file_errors,
        "export_object_errors": export_object_errors,
        "import_file_errors": import_file_errors,
        "import_object_errors": import_object_errors,
    }

    # MATCH PATTERNS
    # export {object1, object2,...} from 'relative_file_path'
    export_obj_from = re.compile(
        r"(?<!//)(?P<whole>export\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
    )
    # export * from 'relative_file_path'
    export_all_from = re.compile(
        r"(?<!//)(?P<whole>export\s+\*\s+from\s+'(?P<file>[^']+)')"
    )
    # export <class/var/func/> object
    export_obj = re.compile(
        r"(?<!//)(?P<whole>export\s+(?:class|var|function|const|let)?\s+(?P<object>\w+\b))"
    )
    # import {object1, object2, ...} from 'relative_file_path'
    import_obj_from = re.compile(
        r"(?<!//)(?P<whole>import\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
    )
    patterns = [
        export_obj_from,
        export_all_from,
        export_obj,
        import_obj_from,
    ]

    dir_path = os.sep.join(
        file_path.split(os.sep)[:-1]
    )
    with open(file_path, "r") as js_file:
        contents = js_file.read()

    for pattern in patterns:
        start_pos = 0
        match = pattern.search(contents, start_pos)
        while match:
            
            if pattern == export_obj_from:
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
                    export_file_errors.append(new_file_path)#match.group("whole"))
                else:
                    for obj in objects:
                        if not obj in search_imports_and_exports(
                                new_file_path,
                                start_file,
                                file_list,
                                file_list_to_display + [current_file]):
                            exports.append(obj)
                        else:
                            export_object_errors.append(match.group("objects"))#match.group("whole"))

            elif pattern == export_all_from:
                relative_file_path = match.group("file")
                new_file_path = os.path.abspath(
                    os.path.join(dir_path, relative_file_path)
                )
                if not os.path.isfile(new_file_path):
                    export_file_errors.append(new_file_path)#match.group("whole"))
                else:
                    exports.extend(
                        search_imports_and_exports(
                                new_file_path,
                                start_file,
                                file_list,
                                file_list_to_display + [current_file]
                        )
                    )

            elif pattern == export_obj:
                #print match.group("object")
                exports.append(match.group("object"))

            elif pattern == import_obj_from:
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
                    import_file_errors.append(new_file_path)#match.group("whole"))
                else:
                    for obj in objects:
                        if not obj in search_imports_and_exports(
                                new_file_path,
                                start_file,
                                file_list,
                                file_list_to_display + [current_file]):
                            import_object_errors.append(obj)

            start_pos = match.end('whole')
            match = pattern.search(contents, start_pos)

    #if check_recursive:# and file_path in file_list[1:]:
        #print file_path
    #    pass#recursive_imports.append("recursive imports")
      #print file_list

    return exports



def test_file_recursion(current_file, start_file, file_list, file_list_to_display, error_found=False):

    if current_file in file_list:
        #file_list.append(current_file)
        if current_file == start_file:
            #print len(file_list)
            #print " "
            #print "\n".join(file_list_to_display + [current_file])
            DATABASE[start_file]["recursive_imports"] = file_list_to_display + [current_file]
            error_found = True
        return
    file_list.append(current_file)

    # MATCH PATTERNS
    # export {object1, object2,...} from 'relative_file_path'
    export_obj_from = re.compile(
        r"(?<!//)(?P<whole>export\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
    )
    # export * from 'relative_file_path'
    export_all_from = re.compile(
        r"(?<!//)(?P<whole>export\s+\*\s+from\s+'(?P<file>[^']+)')"
    )
    # export <class/var/func/> object
    export_obj = re.compile(
        r"(?<!//)(?P<whole>export\s+(?:class|var|function|const|let)?\s+(?P<object>\w+\b))"
    )
    # import {object1, object2, ...} from 'relative_file_path'
    import_obj_from = re.compile(
        r"(?<!//)(?P<whole>import\s+\{(?P<objects>[^\}]+)\}\s+from\s+'(?P<file>[^']+)')"
    )
    patterns = [
        export_obj_from,
        export_all_from,
        import_obj_from,
    ]

    dir_path = os.sep.join(
        current_file.split(os.sep)[:-1]
    )
    with open(current_file, "r") as js_file:
        contents = js_file.read()

    for pattern in patterns:
        start_pos = 0
        match = pattern.search(contents, start_pos)
        while match:

            relative_file_path = match.group("file")
            new_file_path = os.path.abspath(
                os.path.join(dir_path, relative_file_path)
            )
            if os.path.isfile(new_file_path):
                test_file_recursion(
                    new_file_path,
                    start_file,
                    file_list,
                    file_list_to_display+[current_file],
                    error_found=error_found
                )
                # if not error_found:
                #     file_list.pop()

            start_pos = match.end('whole')
            # print match.group("whole")
            # print start_pos
            match = pattern.search(contents, start_pos)



args = parser.parse_args()

relative_path_to_proj_dir = next(iter(args.d), "")
current_dir = os.getcwd()
proj_dir = os.path.abspath(relative_path_to_proj_dir)

for subdir, dirs, files in os.walk(proj_dir):
    for filename in files:
        #print "---------------------"
        filepath = os.path.join(subdir, filename)
        if filepath.endswith(".js") or filepath.endswith(".mjs"):
            search_imports_and_exports(filepath, filepath, [], [])# check_recursive=True)
            #print "\n\n"+filepath+"\n"
            test_file_recursion(filepath, filepath, [], [])


            # js_file = open(filepath, "r")
            # contents = js_file.read()
            # # PATTERN: import {...} from '...js'
            # import_pattern = r"import.*?\{.*?\}.*?from.*?'.*?js'"
            # imports = re.findall(
            #     import_pattern,
            #     contents,
            #     flags=re.DOTALL,
            # )
            # for match in imports:
            #     print match
                
            #     # PATTERN: ...'(...)'
            #     file_pattern = r".*'(.*)'"
            #     relative_path_to_import = re.match(
            #         file_pattern,
            #         match,
            #         flags=re.DOTALL,
            #     ).group(1)
            #     path_to_import = os.path.normpath(
            #         os.path.join(
            #             subdir,
            #             relative_path_to_import
            #         )
            #     )
            #     print path_to_import

                # # PATTERN ...{(...)}
                # objects_pattern = r".*\{(.*)\}"
                # objects_list = re.match(
                #     objects_pattern,
                #     match,
                #     re.DOTALL,
                # ).group(1)
                # print objects_list
                # objects = re.split(
                #     r"[,\s]+",
                #     objects_list,
                # )
                # # remove empty strings
                # objects = [
                #     object for object in objects if object
                # ]
                # print objects

                # import_file = open(path_to_import, "r")
                # import_contents = import_file.read()

            """
                Will need to refactor to turn this into a function to
                allow recursive searching AND
                want to build up a database of each file we've FINISHED
                searching through saying 'this is what this file exports'
                so if we go back to a file that's already been searched
                we can just check if the object is in the database.

                def search_imports(file):
                    # search for objects imported from file
                    import_object_errors = []
                    import_file_errors = []
                    import_syntax_errors = []
                    for each object:
                        if object not in search_exports(filepath):
                            import_object_errors.append(object)

                        if file in EXPORT_DATABASE.keys():
                            if object not in EXPORT_DATABASE[file][exports]:
                                imports_object_errors.append([filepath, object])
                        else:
                            search for 'export (var/class/function/"") object'
                            if found:
                                if match is of form 'export...{...object...} from newfile':
                                    search_imports(object)
                                else:
                                    done (/)
                            else:
                                search 'export * from...':
                                for each found:
                                    search file it's from

                def search_exports(file, database={}):
                    open file
                    search for 'export (var/class/function/""/*) <word>'
                    for each match:
                        if match is "export {...} from 'file'":
                            search_exports(file, database)
                        else if match 

                """

                # print ""


            #break
            
            # for line in lines:
            #     if fnmatch.fnmatch("import {*} from '")
            #     if re.match(r"import {} ", line):
            #         print line

            

            #print filepath

# def search_exports(file_path):
#     """Search for objects exported by file and add to DATABASE.

#     Args:
#         file (str): path to file.

#     Returns:
#         (list(str)) all objects exported by file.
#     """
#     if file_path in EXPORT_DATABASE.keys():
#         return EXPORT_DATABASE[file_path]["exports"]
#     exports = []
#     export_file_errors = []
#     export_object_errors = []
#     export_syntax_errors = []
    # open file
    # search for 'export...'
    # for each match:
    #    if match is "export {object} from 'new file'":
    #        if file doesn't exist:
    #           export_file_errors.append(new file)
    #           continue
    #        if object in search_exports(new file):
    #           exports.append(object)
    #        else:
    #           export_object_errors.append(object)
    #    elif match is "export * from new file":
    #        if file doesn't exist:
    #           export_file_errors.append(new file)
    #           continue
    #        else:
    #           exports.extend(search_exports(new file))
    #    elif match is "export (var/class/function/"") object":
    #         exports.append(object)
    #    else:
    #        syntax is wrong
    #        export_syntax_errors.append(match)
    # EXPORT_DATABASE[file] = {
    #    "exports": export_file_errors,
    #    "export_file_errors": export_file_errors,
    #    "export_object_errors": export_object_errors,
    #    "export_syntax_errors": export_syntax_errors,
    # }
    # return exports




if __name__ == "__main__":
    ERROR_MESSAGE = "IMPORT/EXPORT ERRORS FOUND:\n\n{0}"
    NO_ERROR_MESSAGE = "NO IMPORT/EXPORT ERRORS FOUND"
    DETAILS = ""
    for filename, errors in DATABASE.iteritems():
        file_details = ""
        for error_type, error_list in errors.iteritems():
            if error_type != "exports":
                if error_list:
                    message = "\t" + error_type.upper() + "\n\t\t" + "\n\t\t".join(error_list)
                    file_details += message + "\n"
        if file_details:
            DETAILS += filename + "\n" + file_details + "\n\n"
    MESSAGE = (
        ERROR_MESSAGE.format(DETAILS) 
        if DETAILS
        else NO_ERROR_MESSAGE
    )
    print MESSAGE

#filep = "C:\Users\Ben\Documents\Coding\Javascript\PaintGame\src\Javascript\Utils\constants.mjs"
#filep = "C:\Users\Ben\Documents\Coding\Javascript\PaintGame\\test\exports.mjs"
#test_file_recursion(filep, filep, [], [])


    #other import/export - for syntax_errors, but maybe ignore since will be picked up anyway?


    # open file
    # search for 'export...'
    # for each match:
    #    if match is "export {object} from 'new file'":
    #        if file doesn't exist:
    #           export_file_errors.append(new file)
    #           continue
    #        if object in search_exports(new file):
    #           exports.append(object)
    #        else:
    #           export_object_errors.append(object)
    #    elif match is "export * from new file":
    #        if file doesn't exist:
    #           export_file_errors.append(new file)
    #           continue
    #        else:
    #           exports.extend(search_exports(new file))
    #    elif match is "export (var/class/function/"") object":
    #         exports.append(object)
    #    else:
    #        syntax is wrong
    #        export_syntax_errors.append(match)
    # EXPORT_DATABASE[file] = {
    #    "exports": export_file_errors,
    #    "export_file_errors": export_file_errors,
    #    "export_object_errors": export_object_errors,
    #    "export_syntax_errors": export_syntax_errors,
    # }
    # return exports
