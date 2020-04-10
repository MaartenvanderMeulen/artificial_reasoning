import parsers
import binding


def and_satisfied(and_args, predicates, bindings):
    for arg in and_args:
        is_satisfied, bindings = satisfy(arg, predicates, bindings)
        # print("        and_satisfied", arg, is_satisfied, bindings)
        if not is_satisfied:
            return False, bindings
    return True, bindings


def or_satisfied(and_args, predicates, bindings):
    '''At least 1 arg has to be satisfied'''
    for arg in and_args:
        is_satisfied, extended_bindings = satisfy(arg, predicates, bindings)
        if is_satisfied:
            return True, extended_bindings
    return False, bindings


def satisfy(cond, predicates, bindings):
    '''Can we satisfy the condition in the given context?  A condition is always list.
    Lists have the form [Predicate relation objects ...] [and cond cond cond ...], [or cond cond cond ...], or [cond]'''
    assert type(cond) == type([]) # all conditions are lists
    if len(cond) == 0: # []
        return False, None
    if cond[0] == 'and': # [and, list1, list2, ...]
        return and_satisfied(cond[1:], predicates, bindings)
    if cond[0] == 'or': # [or, ist1, list2, ...]
        return or_satisfied(cond[1:], predicates, bindings)
    if type(cond[0]) == type(""): # Predicate [relation, object1, object2, ...]
        return binding.is_in_predicates(cond, predicates, bindings)
    assert type(cond[0]) == type([]) # [[...]]
    return satisfy(cond[0], predicates, bindings) # [list1, ...] but only first one matters
            

def apply_rules(predicates, rules):
    '''apply rules and return true if predicates get changed'''
    # print("apply_rules", "predicates", predicates, "rules", rules)
    predicates_changed = False
    for condition, conclusion in rules:
        is_satisfied, bindings = satisfy(condition, predicates, [{}]) # [{}] is one empty binding
        # bindings is a list of dicts. Each dict is an alternative binding        
        # print("    condition", condition, "is_satisfied", is_satisfied, "bindings", bindings, "predicates", predicates)
        if is_satisfied:
            for b in bindings:
                predicate = binding.apply_binding(conclusion, b)
                count_unbounded_objects = sum([1 for x in predicate[1:] if x[0] == "_"])
                if count_unbounded_objects == 0 and predicate not in predicates:
                    # print("        add bounded_predicate", bounded_predicate)
                    predicates.append(predicate)
                    predicates_changed = True
    return predicates_changed


def run_forward_reasoning(predicates, rules):
    while apply_rules(predicates, rules):
        pass


def run():
    input_predicates_file = "input_predicates.txt"
    rules_file = "rules.txt"
    output_predicates_file = "output_predicates.txt"
    predicates = parsers.read_predicates(input_predicates_file)
    rules = parsers.read_rules(rules_file)
    run_forward_reasoning(predicates, rules)
    parsers.write_predicates(predicates, output_predicates_file)

if True:
    run()