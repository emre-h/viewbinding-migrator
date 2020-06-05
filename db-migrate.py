fileName = 'MainActivity.java'

bindingName = 'Activity' + fileName.split('Activity')[0] + 'Binding'

commentLines = False

def checkForClass(name):
    lower = False
    upper = False
    for letter in name:
        if not lower:
            lower = letter.islower()
        if not upper:
            upper = letter.isupper()

    return lower and upper


with open(fileName, 'r') as codeClass:
    data = codeClass.read()

    lines = data.split("\n")

    expressions = []
    views = []
    viewIDs = []

    for n, i in enumerate(lines):
        expressions.append(i)
            
    
    for n, j in enumerate(expressions):

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
            else:
                views.append(view[1])

            # views.append(view[1] if len(view) > 1 else view[0])
            
            viewID = assignment[1].strip().split("findViewById")[1].replace(")","").replace("(R.id.","")

            viewIDs.append(viewID.replace(";",""))

            expressions[n] = ''

    for n, e in enumerate(expressions):
        for t, view in enumerate(views):
            if ("findViewById" in e) or (view in e and ((not '.' in e) and (not ')' in e) and (not '(' in e))):
                expressions[n] = ''
            elif view in e and ('.' in e):
                expressions[n] = expressions[n].replace(view,"binding."+viewIDs[t])

    
    for i in expressions:
        print(i)