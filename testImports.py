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
        print ""
        filepath = os.path.join(subdir, filename)
        if filepath.endswith(".js") or filepath.endswith(".mjs"):
            file = open(filepath, "r")
            contents = file.read()
            # PATTERN: import {...} from '...js'
            import_pattern = r"import.*\{.*\}.*from.*'.*js'"
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
                ).group(1)
                path_to_import = os.path.normpath(
                    os.path.join(
                        subdir,
                        relative_path_to_import
                    )
                )
                print path_to_import


            #break
            
            # for line in lines:
            #     if fnmatch.fnmatch("import {*} from '")
            #     if re.match(r"import {} ", line):
            #         print line

            

            #print filepath

