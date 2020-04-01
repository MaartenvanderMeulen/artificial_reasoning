##gewenste toevoegingen
##1. feiten en regels laden vanaf vaste schijf
##2. regel-editor maken
##3. Regels met alternatieve en cumulatieve voorwaarden
##4. uitzonderingen op regels
##5. upgraden naar predikatenlogica



Facts = ['a', 'b', 'c']
Rules = [{'id': 1, 'concl': 'd', 'conds': ['and', 'a', 'c'], 'applied': False},
         {'id': 2, 'concl': 'e', 'conds': ['and', 'b', 'd'], 'applied': False}]

def and_satisfied(c):
    if c == []:
        return(True)
    elif c[0] == 'or':
        return(or_satisfied(c[1:]))
    else:
        andsatisfied = True
        for f in c:
            if f not in Facts:
                andsatisfied = False
                break
        return(andsatisfied)

def or_satisfied(c):
    if c == []:
        return(False)
    elif c[0] == 'and':
        return(and_satisfied(c[1:]))
    else:
        orsatisfied = False
        for f in c:
            if f in Facts:
                orsatisfied = True
                break
        return(orsatisfied)

def satisfied(c):
    if c[0] == 'and': return(and_satisfied(c[1:]))
    elif c[0] == 'or': return(or_satisfied(c[1:]))
    elif c[0] in Facts: return(True)
    else: return(False)

    
#feed forward mechanisme 
def run(): 
    changed = True
    while changed:
        changed = False
        for rule in Rules:
            if not rule['applied']:
                if satisfied(rule['conds']):
                    Facts.append(rule['concl'])
                    rule['applied'] = True
                    changed = True
                    print(Facts)
                else:
                    pass
            else:
                pass

run()