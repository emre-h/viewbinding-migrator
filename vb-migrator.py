import sys
import os
from fnmatch import fnmatch

appPath = sys.argv[1]
fileType = ".java"

print(appPath)

for root, subdirs, files in os.walk(appPath):
    for file in files:
        if not file in subdirs:
            if ".java" in file:
                print(files)
        

def checkForClass(name):
    lower = False
    upper = False

    for letter in name:
        if not lower:
            lower = letter.islower()
        if not upper:
            upper = letter.isupper()

    return lower and upper

def refactorFile(fileName):
    bindingName = 'Activity' + fileName.split('Activity')[0] + 'Binding'

    setContentView = "        binding = " + bindingName + ".inflate(getLayoutInflater());" + "\n        final View view = binding.getRoot();" + "\n        setContentView(view);"

    commentLines = False
    contentViewSet = False
    bindingLateInitVar = False

    with open(fileName, 'r') as codeClass:
        data = codeClass.read()

    lines = data.split("\n")

    views = []
    viewIDs = []
    
    for n, j in enumerate(lines):

        if not contentViewSet:
            if "setContentView" in j:
                lines[n] = setContentView

        if "/*" in j:
            commentLines = True
            continue

        if "*/" in j:
            commentLines = False
            continue

        if "/" in j or commentLines:
            continue

        if "findViewById" in j:
            assignment = j.split("=")
        
            view = assignment[0].strip().split(" ")

            if len(view) > 2:
                for ind, v in enumerate(view):
                    if checkForClass(v):
                        views.append(view[ind + 1])
                        break
            elif len(view) == 2:
                views.append(view[1])
            else:
                views.append(view[0])

            viewID = assignment[1].strip().split("findViewById")[1].replace(")","").replace("(R.id.","")

            viewIDs.append(viewID.replace(";",""))

            lines[n] = ''

    for n, e in enumerate(lines):
        for t, view in enumerate(views):

            if ("findViewById" in e) or (view in e and ((not '.' in e) and (not ')' in e) and (not '(' in e))):
                if not bindingLateInitVar:
                    lines[n] = "    private " + bindingName + " binding;"
                    bindingLateInitVar = True
                else:
                    lines[n] = ''

            elif view in e and ('.' in e):
                lines[n] = lines[n].replace(view,"binding."+viewIDs[t])

    
    
    
    return 1