from subprocess import PIPE, Popen
import sys
import os

def fetchPackageName():
    manifestPath = appPath + "/AndroidManifest.xml"
    with open(manifestPath, 'r') as codeClass:
        xmlArray = codeClass.read().split("\n")

        for i in xmlArray:
            if 'package=' in i:
                return i.replace("package=\"","").replace("\">","").strip()
    
    return ''

sourcePath = sys.argv[1]

rebuildProject = True

try:
    rebuildProject = False if sys.argv[2] == 'false' else True 
except:
    rebuildProject = True

print(rebuildProject)

appPath = sourcePath + "/app/src/main"

javaFileType = ".java"
xmlFileType = ".xml"
ignoreText = "viewBindingIgnore=\"true\""

viewImport = "import android.view.View;"

packageName = fetchPackageName()

bindingImport = "import " + packageName + ".databinding"

generatedBindingFiles = []
javaFiles = []
xmlFiles = []

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def getFiles(dirName, bindingMode):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getFiles(fullPath, False)
        else:
            allFiles.append(fullPath)
            if not bindingMode:
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

def varNameToCamelCase(name):
    if '_' in name:
        arr = name.split("_")
        result = ""
        i = 0

        for k in arr:
            result += k.title() if not i == 0 else k
            i +=1
        return result
    else:
        return name

def refactorFile(fileName):
    pth = fileName.split("/")
    className = pth[len(pth)-1].replace(".java","");

    commentLines = False
    contentViewSet = False

    with open(fileName, 'r') as codeClass:
        data = codeClass.read()

        bindingName = ""

        tmp = className + 'Binding'

        activity = False
        fragment = False
        dialog = False

        if not tmp in generatedBindingFiles:
            if 'Activity' in className:
                tmp = 'Activity' + className.replace('Activity','') + 'Binding'

            elif 'Fragment' in className:
                tmp = 'Fragment' + className.replace('Fragment','') + 'Binding'
            
        bindingName = tmp

        setContentView = "        binding = " + bindingName + ".inflate(getLayoutInflater());" + "\n        final View view = binding.getRoot();" + "\n        setContentView(view);"
        
        fragmentInflatedView = ''
        
        firstBracket = True
        onCreateView = False

        # onCreateViewReturn = False

        bindingImported = False

        if bindingName in data:
            return 0

        if 'extends Activity' in data or 'extends AppCompatActivity' in data:
            activity = True
                
        elif 'extends Fragment' in data:
            fragment = True

        # if 'extends Dialog' in data:
        #    dialog = False

        if not activity and not fragment and not dialog:
            return 0

        viewClassImported = (viewImport in data)

        lines = data.split("\n")

        views = []
        viewIDs = []

        for n, j in enumerate(lines):

            if activity:
                if not contentViewSet:
                    if 'setContentView' in j:
                        lines[n] = setContentView
            elif fragment:
                if not onCreateView:
                    if 'onCreateView' in j:
                        onCreateView = True
                else:
                    if fragmentInflatedView == '':
                        if '.inflate' in j:
                            infArray = j.split('=')[0].strip().split(" ")
                            fragmentInflatedView = infArray[len(infArray) - 1]
                            fragmentBindingView = "        binding = " + bindingName + ".inflate(getLayoutInflater());" + "\n        final View " + fragmentInflatedView + " = binding.getRoot();" + "\n"
                            lines[n] = fragmentBindingView
                    
            if "/*" in j:
                commentLines = True
                continue

            if "*/" in j:
                commentLines = False
                continue

            if commentLines:
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

                viewID = assignment[1].strip().split("findViewById")[1].replace(")","").replace("(R.id.","").replace("(android.R.id.","")

                viewIDs.append(varNameToCamelCase(viewID.replace(";","")))

                lines[n] = ""

        for n, e in enumerate(lines):
            if not viewClassImported:
                if 'import' in e:
                    lines[n] = e + "\n" + viewImport
                    viewClassImported = True

            if viewClassImported and not bindingImported:
                if 'import' in e:
                    lines[n] = e + "\n" + bindingImport + "." + bindingName + ";"
                    bindingImported = True

            if firstBracket:
                if "{" in e:
                    lines[n] = e + "\n    private " + bindingName + " binding;"
                    firstBracket = False

            if 'class' in e:
                continue

            for t, view in enumerate(views):
                insideCheck = (not viewIDs[t] in view) and (not view in viewIDs[t])
                
                if ' ' + view in e and ((not '.' in e) and (not ')' in e) and (not '(' in e)):
                    lines[n] = ''

                elif insideCheck and (' ' + view in e) or ('.' + view in e) and not ('string.' + view in e) or ('(' + view + ')' in e) and not 'void' in e:
                    lines[n] = lines[n].replace(view, "binding." + viewIDs[t])

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

getFiles(appPath, False)

def doGradleTasks():
    if not rebuildProject:
        return 1

    clean = "./gradlew clean"
    build = "./gradlew assembleDebug"
    baseCommand = "cd " + "\"" + sourcePath + "\"" " && chmod +x gradlew && "

    print("Cleaning project...\n")
    outClean = str(cmdline(baseCommand + clean),'utf8')

    if ('BUILD SUCCESSFUL' in outClean):
        print("Project has been cleaned successfully\n")
        print("Building project...")

        outBuild = str(cmdline(baseCommand + build),'utf8')

        if ('BUILD SUCCESSFUL' in outBuild):
            print("Project has been built successfully\n")
            print("Refactoring Java files...\n")
            return 1
        else:
            return 0
    else:
            return 0
    
for i in xmlFiles:
    result = removeIgnoreBinding(i)

    if result == 0:
        print("Ignored XML file:" + i)
        continue
    else:
        writeFile(i,result)
        print("Refactored XML layout: " + i)

def refactorClasses():
    for i in javaFiles:

        if not 'FeaturesFragment' in i:
            continue

        result = refactorFile(i)

        if result == 0:
            print("Ignored Java file:" + i)
            continue
        else:
            writeFile(i,result)
            print("Refactored Java file: " + i)

if doGradleTasks() == 1:
    pkgArray = packageName.split(".")

    pkgPath = ""

    for part in pkgArray:
        pkgPath = pkgPath + part + "/"

    generatedBindingFiles = getFiles(sourcePath + "/app/build/generated/data_binding_base_class_source_out/debug/out/" + pkgPath + "databinding", True)

    for i in range(0,len(generatedBindingFiles)):
        generatedBindingFiles[i] = generatedBindingFiles[i].replace(sourcePath + "/app/build/generated/data_binding_base_class_source_out/debug/out/" + pkgPath + "databinding/","").replace(".java","")

    refactorClasses()