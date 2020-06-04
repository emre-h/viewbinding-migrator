fileName = 'MainActivity.java'

bindingName = 'Activity' + fileName.split('Activity')[0] + 'Binding'

with open(fileName, 'r') as codeClass:
    data = codeClass.read()

    lines = data.split("\n")

    expressions = []
    views = []
    viewIDs = []
    semicolonRowIndexes = []
    semicolonColumnIndexes = []
    willBeDeletedIndexes = []

    for n, i in enumerate(lines):
        if ';' in i:
            semicolonRowIndexes.append(n)
            semicolonColumnIndexes.append(i.index(";"))
        splittedVar = i.split(";")

        for e in splittedVar:
            expressions.append(e)
    
    for n, j in enumerate(expressions):

        if "/" in j:
            continue

        if "findViewById" in j:
            assignment = j.split("=")
        
            views.append(assignment[0].strip())
            
            viewID = assignment[1].strip().split("findViewById")[1].replace(")","").replace("(R.id.","")

            viewIDs.append(viewID)

            willBeDeletedIndexes.append(n)

            expressions[n] = ''

    for n, e in enumerate(expressions):
        for view in views:
            if ("findViewById" in e) or (view in e and (not '.' in e) and (not ')' in e) and (not '(' in e)):
                expressions[n] = ''

                willBeDeletedIndexes.append(n)
      

    for m, o in enumerate(semicolonRowIndexes):
        if n in willBeDeletedIndexes:
            continue
        
        if n == o:
            e = expressions[o]
            ind = semicolonColumnIndexes[m]
            expressions[o] = e[:ind] + ';' + e[ind:]

    for i in expressions:
        print(i)