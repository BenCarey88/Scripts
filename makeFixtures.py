import sys
import os
import argparse

parser = argparse.ArgumentParser(
    description="Make fixture files for javascript testing."
)
parser.add_argument(
    "fixture_name",
    metavar="fixture name",
    type=str,
    nargs=1,
    help="name of fixture to add"
)
parser.add_argument(
    "-n", "--nesting",
    metavar="[level]",
    action="store",
    type=int,
    nargs=1,
    default=[1],
    help="level of nesting (default 1)"
)
parser.add_argument(
    "-t", "--test",
    metavar="[name]",
    action="append",
    dest="tests",
    default=[],
    type=str,
    help="add fixture to test in this directory"
)
parser.add_argument(
    "-at", "--add_to_all",
    action="store_const",
    default=False,
    const=True,
    help="add fixture to all tests in this directory"
)

# arg parser
args = parser.parse_args()

# fixture name
def formatNames(arg_name):
    argName = arg_name[0].lower() + arg_name[1:]
    ArgName = arg_name[0].upper() + arg_name[1:]
    return argName, ArgName

fixture_name = args.fixture_name[0]
fixtureName, FixtureName = formatNames(fixture_name)

#nesting
nestingLevel = args.nesting[0]
nesting = "/".join([".." for i in range(nestingLevel + 1)])
lesserNesting = "/".join([".." for i in range(nestingLevel)]) or "."
indents = "".join("\t" for i in range(nestingLevel))

os.mkdir("Fixtures")
currentDirPath = os.getcwd()
tests = (
    args.tests if not args.add_to_all else
    os.listdir(currentDirPath)
)

#create .html file
htmlFile = open("Fixtures/{0}.html".format(fixtureName), "w+")
htmlFileContents = [
    "<!DOCTYPE html>",
    "<html>",
    "<head>",
	"\t<meta charset='utf-8' />",
	"\t<title>{0}</title>".format(FixtureName),
	"\t<link rel='stylesheet' type='text/css' href='{0}/fixture.css' />".format(nesting),
    "</head>",
    "<body>",
    "",
    "\t<canvas id='myCanvas' width = '1500' height = '1000' ></canvas>"
    "",
	"\t<script src = './main.js' type = 'module'></script>",
    "",
    "</body>",
    "</html>",
]
htmlFile.write("\n".join(htmlFileContents))
htmlFile.close()


#create base for .mjs test class file
mjsFile = open("Fixtures/{0}.mjs".format(fixtureName), "w+")
mjsFileContents = [
    "import {{Fixture}} from '{0}/fixture.mjs'".format(nesting),
    "",
    "export var fixture = new Fixture("
    "\t{",
    "",
    "\t}"
    ");",
]
mjsFile.write("\n".join(mjsFileContents))
mjsFile.close()


#create main .js file to be called by .html file
mainFile = open("Fixtures/main.js", "w+")
mainFileContents = [
    "//draw fixture objects to ctx",
    "",
    "import {{fixture}} from './{0}.mjs';".format(fixtureName),
    "import {{printColour, newLine, addLink}} from '{0}/exports.mjs';".format(nesting),
    "",
    "var canvas = document.getElementById('myCanvas');",
    "var ctx = canvas.getContext('2d');"
    "",
    "fixture.draw(ctx, true);",
    "",
    "newLine();",
    "printColour('All Tests', 'white');",
    "addLink('All Tests', '{0}/test.html');".format(nesting),
]
mainFile.write("\n".join(mainFileContents))
mainFile.close()


#create index .mjs file for calling fixture
indexFile = open("Fixtures/index.mjs", "w+")
indexFileContents = [
    "export * from './{0}.mjs';".format(fixtureName),
]
indexFile.write("\n".join(indexFileContents))
indexFile.close()


#append fixture to test files
for test_name in tests:
    testName, TestName = formatNames(test_name)
    try:
        testMainFile = open("{0}/main.js".format(TestName), "a")
        summaryFileAdditions = [
            "",
            "newLine()",
            "printColour(\"Fixtures\", \"white\")",
            "addLink('Fixtures', '../Fixtures/{0}.html')".format(
                fixtureName
            ),
        ]
    except:
        try:
            testMainFile = open("main.js", "a")
            summaryFileAdditions = [
                "",
                "newLine()",
                "printColour(\"Fixtures\", \"white\")",
                "addLink('Fixtures', '../Fixtures/{0}.html')".format(
                    fixtureName
                ),
            ]
        except:
            continue
    testMainFile.write("\n".join(summaryFileAdditions))
    testMainFile.close()
