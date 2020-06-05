import sys
import os

appPath = sys.argv[1] + "/app/src/main"

javaFileType = ".java"
xmlFileType = ".xml"
ignoreText = "viewBindingIgnore=\"true\""

javaFiles = []
xmlFiles = []

def getFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getFiles(fullPath)
        else:
            allFiles.append(fullPath)
            if javaFileType in fullPath:
                javaFiles.append(fullPath)

            elif xmlFileType in fullPath and 'layout' in fullPath:
                xmlFiles.append(fullPath)
                
    return allFiles

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
    firstBracket = True

    with open(fileName, 'r') as codeClass:
        data = codeClass.read()
        activity = False
        fragment = False
        dialog = False

        if 'extends Activity' in data or 'extends AppCompatActivity' in data or 'setContentView' in data:
            activity = True

        if 'extends Fragment' in data:
            fragment = False

        if 'extends Dialog' in data:
            dialog = False

        if not activity and not fragment and not dialog:
            return 0

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

            if commentLines:
                continue

            if "*/" in j:
                commentLines = False
                continue

            if "//" in j or commentLines:
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

                if e == "{" and firstBracket:
                    lines[n] = "\n    private " + bindingName + " binding;"
                    firstBracket = False

                if ("findViewById" in e) or (view in e and ((not '.' in e) and (not ')' in e) and (not '(' in e))):
                    lines[n] = ''

                elif view in e and ('.' in e):
                    lines[n] = lines[n].replace(view,"binding."+viewIDs[t])

    return lines

# if return is zero, continue.

def removeIgnoreBinding(xmlFile):
    with open(xmlFile, 'r') as xmlClass:
        data = xmlClass.read()
        result = []

        if ignoreText in data:

            splittedData = data.split("\n")

            for i in range(0,len(splittedData)):
                buf = splittedData[i]

                if ignoreText in buf:

                    if ">" in buf:
                        splittedData[i-1] += ">"

                    splittedData[i] = ""

                result = splittedData

        else:
            return 0

    return result
        
def writeFile(path, strlist):    
    with open(path, mode='wt', encoding='utf-8') as f:
        f.write('\n'.join(strlist))

    return 1

getFiles(appPath)
 
for i in xmlFiles:
    result = removeIgnoreBinding(i)

    if result == 0:
        continue
    else:
        writeFile(i,result)
        print("Refactored XML layout: " + i)

for i in javaFiles:
    # print(i)
    result = refactorFile(i)
    print(result)
    if result == 0:
        continue
    else:
        writeFile(i,result)
        print("Refactored Java file: " + i)
