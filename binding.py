def apply_binding(predicate, binding):
    '''return bounded predicate
    ARGS
        binding is a dict'''
    result = [predicate[0]]
    for x in predicate[1:]:
        result.append(binding[x] if x in binding else x)
    return result
    
    
def equal_dict(a, b):
    for key, value in a.items():
        if key not in b or b[key] != value:
            return False
    for key, value in b.items():
        if key not in a or a[key] != value:
            return False
    return True
    

def add_binding(binding, extra_binding, new_bindings):
    '''Merge binding dict with extra_binding_dict, '''
    result = dict()
    for key, value in binding.items():
        result[key] = value
    for key, value in extra_binding.items():
        result[key] = value
    already_present = False
    for x in new_bindings:
        if equal_dict(x, result):
            already_present = True
            break
    if not already_present:
        new_bindings.append(result)
    
        
def is_in_predicates(this_predicate, predicates, current_bindings):    
    debug = False
    if debug:
        print("            is_in_predicates start this_predicate", this_predicate, "predicates", predicates, "current_bindings", current_bindings)
    found = False
    new_bindings = [{}]
    for binding in current_bindings:
        this_bounded_predicate = apply_binding(this_predicate, binding)
        if debug:
            print("            this_bounded_predicate", this_bounded_predicate, "binding", binding)
        for some_predicate in predicates:
            if this_bounded_predicate[0] == some_predicate[0]:
                working_copy = list(this_bounded_predicate)
                assert len(working_copy) == len(some_predicate)
                extra_binding = dict()
                match = True
                for i in range(1, len(working_copy)):
                    if working_copy[i][0] == "_": # unbounded variable
                        extra_binding[working_copy[i]] = some_predicate[i]
                        working_copy = apply_binding(this_predicate, {working_copy[i]: some_predicate[i]})
                        if debug:
                            print("            working copy after temp binding", working_copy)
                    elif working_copy[i] != some_predicate[i]:
                        match = False
                        break
                if not match:
                    continue
                found = True
                if len(extra_binding) > 0:
                    add_binding(binding, extra_binding, new_bindings)                    
    if debug:
        print("            is_in_predicates end. found", found, "new_bindings", new_bindings)
    return found, new_bindings


if False:
    # Testcase 1
    # P(a, c)
    # P(b, d)
    # P(b, e)
    # Q(b, f)
    # if P(_x, _y) and Q(_x, _z) then R(_y)
    this_predicate = ["Q", "_x", "_z"]
    predicates = [["P", "a", "c"], ["P", "b", "d"], ["P", "b", "e"], ["Q", "b", "f"]]
    current_bindings = [{"_x": "a", "_y": "c"}, {"_x": "b", "_y": "d"}, {"_x": "b", "_y": "e"}]
    found, new_bindings = is_in_predicates(this_predicate, predicates, current_bindings)
    # True, [{"_x": "b", "_y": "d", "_z": "f"}, {"_x": "b", "_y": "e", "_z": "f"}]
    print("Testcase 1", found, new_bindings)

if False:
    # Testcase 2
    # P(a, c)
    # P(b, d)
    # P(b, e)
    # Q(b, f)
    # Q(b, g)
    # if P(_x, _y) and Q(_x, _z) then R(_y)
    this_predicate = ["Q", "_x", "_z"]
    predicates = [["P", "a", "c"], ["P", "b", "d"], ["P", "b", "e"], ["Q", "b", "f"],  ["Q", "b", "g"]]
    current_bindings = [{"_x": "a", "_y": "c"}, {"_x": "b", "_y": "d"}, {"_x": "b", "_y": "e"}]
    found, new_bindings = is_in_predicates(this_predicate, predicates, current_bindings)
    # True, [{"_x": "b", "_y": "d", "_z": "f"}, {"_x": "b", "_y": "e", "_z": "f"} and also for g]
    print("Testcase 2", found, new_bindings)


if False:
    # Testcase 3
    # P(a, c)
    # P(b, d)
    # if P(_x, _y) then R(_y)
    this_predicate = ["P", "_x", "_y"]
    predicates = [["P", "a", "c"], ["P", "b", "d"], ]
    current_bindings = [{}]
    found, new_bindings = is_in_predicates(this_predicate, predicates, current_bindings)
    # True, [{"_x": "a", "_y": "c", }, {"_x": "b", "_y": "d"}]
    print("Testcase 3", found, new_bindings)
