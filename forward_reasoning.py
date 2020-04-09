import sys
import utils


def and_satisfied(and_args, facts):
    for arg in and_args:
        if not satisfied(arg, facts):
            return False
    return True


def or_satisfied(and_args, facts):
    '''At least 1 arg has to be satisfied'''
    for arg in and_args:
        if satisfied(arg, facts):
            return True
    return False


def satisfied(cond, facts):
    '''Can we satisfy the condition?  A condition is either a fact or a list.
    Lists have the form [and cond cond cond ...], [or cond cond cond ...], or [cond]'''
    if type(cond) == type([]): # The condition is a list
        if len(cond) == 0: # []
            return False
        if cond[0] == 'and': # [and, fact_or_list1, fact_or_list2, ...]
            return and_satisfied(cond[1:], facts)
        if cond[0] == 'or': # [or, fact_or_list1, fact_or_list2, ...]
            return or_satisfied(cond[1:], facts)
        return satisfied(cond[0], facts) # [fact_or_list1, ...] but only first one matters
    return cond in facts # A condition is either a list or a fact


def apply_rules(facts, rules):
    '''apply rules and return true if facts get changed'''
    facts_changed = False
    for rule in rules:
        if satisfied(rule[0], facts):
            if rule[1] not in facts:
                facts.add(rule[1])
                facts_changed = True
    return facts_changed


def run_forward_reasoning(facts, rules):
    while apply_rules(facts, rules):
        pass


def run():
    input_facts_file = "input_facts.txt"
    rules_file = "rules.txt"
    output_facts_file = "output_facts.txt"
    facts = utils.read_facts(input_facts_file)
    rules = utils.read_rules(rules_file)
    run_forward_reasoning(facts, rules)
    utils.write_facts(facts, output_facts_file)

run()