"""Script to remove all pycache files from all subdirectories."""

import os
import shutil

current_directory = os.getcwd()

for subdir, dirs, files in os.walk(current_directory):
    for dirname in dirs:
        if dirname == "__pycache__":
            path = os.path.join(subdir, dirname)
            print ("Removing directory {0}".format(path))
            shutil.rmtree(path)
    for filename in files:
        if filename.endswith(".pyc"):
            path = os.path.join(subdir, filename)
            print ("Removing file {0}".format(path))
            os.remove(path)
