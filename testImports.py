import argparse
import os
import os.path
import re
import sys

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

args = parser.parse_args()

relative_path_to_proj_dir = next(iter(args.d), "")
current_dir = os.getcwd()
proj_dir = os.path.abspath(relative_path_to_proj_dir)

for subdir, dirs, files in os.walk(proj_dir):
    for filename in files:
        print "---------------------"
        filepath = os.path.join(subdir, filename)
        if filepath.endswith(".js") or filepath.endswith(".mjs"):
            js_file = open(filepath, "r")
            contents = js_file.read()
            # PATTERN: import {...} from '...js'
            import_pattern = r"import.*?\{.*?\}.*?from.*?'.*?js'"
            imports = re.findall(
                import_pattern,
                contents,
                flags=re.DOTALL,
            )
            for match in imports:
                print match
                
                # PATTERN: ...'(...)'
                file_pattern = r".*'(.*)'"
                relative_path_to_import = re.match(
                    file_pattern,
                    match,
                    flags=re.DOTALL,
                ).group(1)
                path_to_import = os.path.normpath(
                    os.path.join(
                        subdir,
                        relative_path_to_import
                    )
                )
                print path_to_import

                # PATTERN ...{(...)}
                objects_pattern = r".*\{(.*)\}"
                objects_list = re.match(
                    objects_pattern,
                    match,
                    re.DOTALL,
                ).group(1)
                print objects_list
                objects = re.split(
                    r"[,\s]+",
                    objects_list,
                )
                # remove empty strings
                objects = [
                    object for object in objects if object
                ]
                print objects

                import_file = open(path_to_import, "r")
                import_contents = import_file.read()

                """
                Will need to refactor to turn this into a function to
                allow recursive searching AND
                want to build up a database of each file we've FINISHED
                searching through saying 'this is what this file exports'
                so if we go back to a file that's already been searched
                we can just check if the object is in the database.

                def search_imports(objects, file, database={}):
                    open file.
                    for each object:
                        if import file already searched:
                            if object not in import_file_database:
                                faulty_imports.append([filepath, object])
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

                print ""


            #break
            
            # for line in lines:
            #     if fnmatch.fnmatch("import {*} from '")
            #     if re.match(r"import {} ", line):
            #         print line

            

            #print filepath

