"""Script to make tests for my javascript paint game."""

import sys
import os
import argparse

parser = argparse.ArgumentParser(
    description="Make test files for javascript testing."
)
parser.add_argument(
    "test_name",
    metavar="test name",
    type=str,
    nargs=1,
    help="name of test to add"
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
    "-f", "--fixture",
    metavar="[name]",
    action="store",
    default=[False],
    type=str,
    nargs=1,
    help="add fixture"
)
parser.add_argument(
    "-fn", "--fixture_nesting",
    metavar="[level]",
    action="store",
    default=[1],
    type=str,
    nargs=1,
    help="level of nesting of fixture (default 1)"
)

# arg parser
args = parser.parse_args()

# test name
test_name = args.test_name[0]
testName = test_name[0].lower() + test_name[1:]
TestName = test_name[0].upper() + test_name[1:]

#nesting
nestingLevel = args.nesting[0]
nesting = "/".join([".." for i in range(nestingLevel + 1)])
lesserNesting = "/".join([".." for i in range(nestingLevel)]) or "."
indents = "".join("\t" for i in range(nestingLevel))

#fixture nesting
fixtureNestingLevel = args.fixture_nesting[0]
fixtureNesting = "/".join([".." for i in range(fixtureNestingLevel)])

os.mkdir(TestName)
currentDirPath = os.getcwd()
relativePathList = (
    [] if nestingLevel == 0 else
    currentDirPath.split("\\")[-nestingLevel:]
)
if relativePathList:
    relativePath = "./" + "".join(relativePathList) + "/" + TestName
else:
    relativePath = "./" + TestName


#create .html file
htmlFile = open("{0}/{1}.html".format(TestName, testName), "w+")
htmlFileContents = [
    "<!DOCTYPE html>",
    "<html>",
    "<head>",
	"\t<meta charset='utf-8' />",
	"\t<title>{0}</title>".format(TestName),
	"\t<link rel='stylesheet' type='text/css' href='{0}/test.css' />".format(nesting),
    "</head>",
    "<body>",
    "",
	"\t<script src = './main.js' type = 'module'></script>",
    "",
    "</body>",
    "</html>",
]
htmlFile.write("\n".join(htmlFileContents))
htmlFile.close()


#create base for .mjs test class file
mjsFile = open("{0}/{1}.mjs".format(TestName, testName), "w+")
mjsFileContents = [
    "import {{Tests}} from '{0}/tests.mjs';".format(nesting),
    "",
    "export class {0} extends Tests {{".format(TestName),
    "\tconstructor() {",
    "\t\tsuper();",
    "\t}",
    "",
    "}",
]
mjsFile.write("\n".join(mjsFileContents))
mjsFile.close()


#create main .js file to be called by .html file
mainFile = open("{0}/main.js".format(TestName), "w+")
mainFileContents = [
    "import {{{0}}} from './{1}.mjs';".format(TestName, testName),
    "import {{run}} from '{0}/tests.mjs';".format(nesting),
    "import {{printColour, newLine, addLink}} from '{0}/exports.mjs'".format(nesting),
    "",
    "run({0});".format(TestName),
    "",
]
if args.fixture:
    mainFileContents.extend([
        "newLine()",
        "printColour(\"Fixtures\", \"white\")",
        "addLink('Fixtures', '{0}/Fixtures/{1}.html')".format(
            fixtureNesting, args.fixture[0],
        ),
    ])
mainFileContents.extend([
    "",
    "newLine()",
    "printColour(\"All Tests\", \"white\")",
    "addLink('All Tests', '{0}/test.html')".format(nesting)
])
mainFile.write("\n".join(mainFileContents))
mainFile.close()


#append text to summary file
summaryFile = open("{0}/main.js".format(lesserNesting), "a")
summaryFileAdditions = [
    "",
    "{0}import {{{1}}} from '{2}/{3}.mjs'".format(
        indents, TestName,  relativePath, testName
    ),
    "{0}runTests({1}, '{2}/{3}.html')".format(
        indents, TestName,  relativePath, testName
    ),
    "",
]
summaryFile.write("\n".join(summaryFileAdditions))
summaryFile.close()
