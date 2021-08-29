
import os

DIRECTORY = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../Javascript/PaintGame_practice"
    )
)

print DIRECTORY

for subdir, dirs, files in os.walk(DIRECTORY):
    for filename in files:
        filepath = os.path.join(subdir, filename)
        if filepath.endswith(".mjs"):
            new_filepath = os.path.join(
                subdir,
                filename.rstrip("mjs") + "js"
            )
            #print "OLD FILE: ", filepath, "\nNEW_FILE: ", new_filepath, "\n\n"
            os.rename(filepath, new_filepath)
