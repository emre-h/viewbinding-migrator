fileName = 'MainActivity.java'

with open(fileName, 'r') as codeClass:
    data = codeClass.read()

    lines = data.replace("{","").replace("}","").split("\n")

    onCreate = False

    expressions = []
    views = []
    viewIDs = []

    for i in lines:
        splitted = i.strip().split(";")
        for e in splitted:
            expressions.append(e.strip())
    

    for j in expressions:

        if "/" in j:
            continue

        #print(j)

        if "findViewById" in j:
            assignment = j.split("=")
        
            views.append(assignment[0].strip())
            
            viewID = assignment[1].strip().split("findViewById")[1].replace(")","").replace("(R.id.","")

            viewIDs.append(viewID)


print(viewIDs)

print(views)