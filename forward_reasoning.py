'''Forward reasoning system.  Run with "python forward_reasoning.py'''


# =================== start parsers ===========================================


class Node:
    '''Datastructure for the backtracking'''
    
    def __init__(self, node_type, childs):
        '''Initialize a Node object'''
        self.node_type = node_type
        assert  node_type in ["and", "or", "()", "predicate"]
        self.childs = childs
        assert type(self.childs) == type([])
        self.index = 0 # self.childs[self.index] is where the backtracking will continue
        
    def __str__(self):
        '''Convert a Node object to a string'''
        childs_str = [str(child) for child in self.childs]
        return "(" + self.node_type + "," + ",".join(childs_str) + "," + str(self.index) + ")"
        
    def append_child(self, child):
        '''Append child to Node.  In the future some extra bookkeeping may be done here, like setting the parent of each child.'''
        self.childs.append(child)
        
        
class Rule:
    def __init__(self, condition, conclusion):
        '''Initialize a Rule object'''
        self.condition = condition
        self.conclusion = conclusion
        
    def __str__(self):
        '''Convert a Rule object to a string'''
        return "if " + str(self.condition) + " then " + str(self.conclusion)


class Parser:
    '''Parsers to read predicates and rules from text files
    Predicate "P(x,y)" is converted to Node("predicate", '["P", "x", "y"]')    
    Rule "if P(x,y) then Q(z)" is converted to [Node("Predicate",'["P", "x", "y"]'), Node("predicate", '["Q", "z"]']
    '''
    def __init__(self):
        '''Initialize a Parser object'''
        self.end_of_line = ""
        self.keywords = set(["if", "then", "and", "or"])

    # ====================== INTERNAL FUNCTIONS =====================
    
    def _tokenize(line):
        '''break string into list of tokens.  Remove empty tokens that are just separetors.'''
        for sep in ["(", ")", "#", ]:
            line = line.replace(sep, " " + sep + " ")
        for sep in [",", "'", ]:
            line = line.replace(sep, " ")
        tokens = [token for token in line.split(" ") if token != '']
        result = []
        for token in tokens:
            if token.lower() in ["if", "and", "or", "then",]:
                token = token.lower()
            result.append(token)
        return result

    def _first_token(self):
        '''Go to the first token'''
        if len(self.tokens) > 0:
            self.i = 0
            self.token = self.tokens[self.i]
        else:
            self.token = self.end_of_line

    def _next_token(self):
        '''Go to the next token'''
        if len(self.tokens) > self.i + 1:
            self.i += 1
            self.token = self.tokens[self.i]
        else:
            self.token = self.end_of_line

    def _token_to_str(self, token):
        '''Convert token to string.  Only makes a difference for the end-of-line token.'''
        return token if token != self.end_of_line else "end-of-line"

    def _expect_token(self, expected):
        '''Read the expevcted token or give an error if it was nog there.'''
        if self.token != expected:
            raise RuntimeError(f"'{self._token_to_str(expected)}' expected instead of '{self._token_to_str(self.token)}'")
        self._next_token()

    def _parse_predicate(self):
        '''Parse a predicate (a predicate start is expected under self.token)'''
        if not self.token.isidentifier():
            raise RuntimeError(f"Identifier expected instead of '{self._token_to_str(self.token)}'")        
        predicate = [self.token]
        self._next_token()
        self._expect_token("(")
        while self.token != ")":
            if not self.token.isidentifier():
                raise RuntimeError(f"Identifier expected instead of '{self._token_to_str(self.token)}'")        
            predicate.append(self.token)
            self._next_token()
        self._expect_token(")")
        return Node("predicate", predicate)
            
    def _parse_factor(self):
        '''the 'factor' in recursive descent expression parsing terminology'''
        if self.token == "(":
            self._next_token()
            result = Node("()", [self._parse_expression()])
            self._expect_token(")")
        else:
            result = self._parse_predicate()
        return result

    def _parse_term(self):
        '''the 'term' in recursive descent expression parsing terminology'''
        result = self._parse_factor()
        if self.token == "and":
            result = Node("and", [result])
            while self.token == "and":
                self._next_token()
                result.append_child(self._parse_factor())
        return result

    def _parse_expression(self):
        '''the 'expression' in recursive descent expression parsing terminology'''
        result = self._parse_term()
        if self.token == "or":
            result = Node("or", [result])
            while self.token == "or":
                self._next_token()
                result.append_child(self._parse_term())
        return result
        
    # ====================== PUBLIC INTERFACE =====================
    
    def parse_predicate(self, line):
        '''Parse the Predicate in the line (string).  Result is a Node object.'''
        self.tokens = Parser._tokenize(line)
        self._first_token()
        if self.token in [self.end_of_line, "#"]:
            return None
        predicate = self._parse_predicate()
        self._expect_token(self.end_of_line)
        return predicate

    def parse_rule(self, line):
        '''Parse the rule in the line (string).  Result is a Rule object.'''
        self.tokens = Parser._tokenize(line)
        self._first_token()
        if self.token in [self.end_of_line, "#"]:
            return None
        self._expect_token("if")
        cond = self._parse_expression()
        self._expect_token("then")
        predicate = self._parse_predicate()
        self._expect_token(self.end_of_line)
        return Rule(cond, predicate)


def read_predicates(input_predicates_file):
    '''Read list of predicates.  Each predicate is a list like ["P", "a", "b"], not a Node object.'''
    result = []
    parser = Parser()
    with open(input_predicates_file, "r") as f:
        line_nr = 0
        for line in f:
            line_nr += 1
            try:
                predicate = parser.parse_predicate(line.strip())
                if predicate is not None:
                    result.append(predicate.childs)
            except RuntimeError as e:
                print(f"{input_predicates_file}, line {line_nr}: {str(e)}")
    return result


def read_rules(rules_file):
    '''Read list of rules.  Each rule is a Rule object with condition and conclusion members.'''
    result = []
    parser = Parser()
    with open(rules_file, "r") as f:
        line_nr = 0
        for line in f:
            line_nr += 1
            try:
                rule = parser.parse_rule(line.strip())
                if rule is not None:
                    result.append(rule)
            except RuntimeError as e:
                print(f"{rules_file}, line {line_nr}: {str(e)}")                
    return result


def write_predicates(predicates, output_predicates_file):
    '''Write the predicates to file.  Predicates are here just lists, not Node objects.'''
    with open(output_predicates_file, "w") as f:
        for predicate in predicates:
            f.write(f"{predicate[0]}(" + ", ".join(predicate[1:]) + ")\n")


# =================== end parsers, begin forward reasoning ====================


class Reasoning:
    '''Object that can do forward reasoning.  Usage: call function derive_all_conclusions()'''
    
    def __init__(self, predicates):
        self.predicates = predicates
        assert len(self.predicates) > 0 # otherwise no predicate is true
    
    # ====================== INTERNAL FUNCTIONS =====================
    
    def apply_bindings(self, predicate, bindings):
        '''apply dict with bindings like {"_x": "a"} to predicate like ["P", "_x", "_y"] resulting in ["P", "a", "_y"]
        ARGS
            predicate: is the predicate to be bound
            bindings: dict with entries like {"_x": "a"}'''
        result = [predicate[0]]
        for x in predicate[1:]:
            result.append(bindings[x] if x[0] == "_" and x in bindings else x)
        return result
        
    def is_valid_predicate(self, node):    
        '''Does node matches self.predicates[node.index]?'''
        working_copy = self.apply_bindings(node.childs, self.bindings)
        assert node.index < len(self.predicates)
        database_row = self.predicates[node.index]
        if working_copy[0] != database_row[0]: # different predicate
            return False
        assert len(working_copy) == len(database_row)
        for i in range(1, len(working_copy)): # go over all objects of the predicate
            if working_copy[i][0] == "_": # unbounded variable
                self.bindings[working_copy[i]] = database_row[i]
                working_copy[i] = database_row[i]
            elif working_copy[i] != database_row[i]:
                return False
        return True

    def is_valid_condition(self, node):
        '''Does the current experiment makes node valid?'''
        if node.node_type == 'and':            
            for i in range(len(node.childs)):
                if not self.is_valid_condition(node.childs[i]):
                    return False
            return True
        if node.node_type == 'or':
            return self.is_valid_condition(node.childs[node.index])
        if node.node_type == 'predicate':
            return self.is_valid_predicate(node)
        assert node.node_type == '()'
        return self.is_valid_condition(node.childs[0]) # [[ ...
        
    def draw_conclusion(self):
        '''Use the bindings that made this experiment valid for the conclusion.'''
        bounded_conclusion = self.apply_bindings(self.conclusion.childs, self.bindings)
        if bounded_conclusion not in self.conclusions and bounded_conclusion not in self.predicates:
            self.conclusions.append(bounded_conclusion)
        
    def reset_experiments(self, node):
        '''Experiment : each logical sub-expression that could make self.condition valid is called an "experiment".'''
        '''Go to the first experiment.'''
        node.index = 0
        if node.node_type in ['and', 'or', '()']:
            for child in node.childs:
                self.reset_experiments(child)
        else: # predicate
            while node.index < len(self.predicates) - 1:
                if node.childs[0] == self.predicates[node.index][0]:
                    return
                node.index += 1
    
    def next_experiment(self, node):
        '''Experiment : each logical sub-expression that could make self.condition valid is called an "experiment".'''
        '''Go to the next experiment.'''
        if node.node_type == '()':
            return self.next_experiment(node.childs[0])
        if node.node_type == 'and':            
            i = len(node.childs) - 1
            while i >= 0:
                if self.next_experiment(node.childs[i]):
                    return True
                self.reset_experiments(node.childs[i])
                i -= 1
            return False
        if node.node_type == 'or':
            if self.next_experiment(node.childs[node.index]):
                return True
            self.reset_experiments(node.childs[node.index])
            node.index += 1
            if node.index >= len(node.childs):
                return False
            self.reset_experiments(node.childs[node.index])
            return True
        assert node.node_type == 'predicate'
        node.index += 1
        while node.index < len(self.predicates):
            if node.childs[0] == self.predicates[node.index][0]:
                return True
            node.index += 1
        return False
        
    # ====================== PUBLIC INTERFACE =====================
    
    def derive_all_conclusions(self, condition, conclusion):
        '''Return all conclusions hat can be drawn'''
        self.condition = condition
        self.conclusion = conclusion
        self.conclusions = []
        self.reset_experiments(self.condition)        
        while True:
            self.bindings = dict()
            if self.is_valid_condition(self.condition):
                self.draw_conclusion()
            if not self.next_experiment(self.condition):
                break
        return self.conclusions
                
            

def apply_rules(predicates, rules):
    '''Run the forward reasoning on the given predicates and rules and add conclusions to the predicates
    RETURNS: True if we could conclude something new'''
    orig_len_predicates = len(predicates)
    reasoning = Reasoning(predicates)
    for rule in rules:
        conclusions = reasoning.derive_all_conclusions(rule.condition, rule.conclusion)
        predicates.extend(conclusions)
    return len(predicates) > orig_len_predicates


def run_forward_reasoning(predicates, rules):
    '''Run the forward reasoning on the given predicates and rules and add conclusions to the predicates'''
    while apply_rules(predicates, rules):
        pass


def run(input_predicates_file, rules_file, output_predicates_file):
    '''Run the forward reasoning on the given files and write the result in the output file'''
    predicates = read_predicates(input_predicates_file)
    rules = read_rules(rules_file)    
    run_forward_reasoning(predicates, rules)    
    write_predicates(predicates, output_predicates_file)


run("input_predicates.txt", "rules.txt", "output_predicates.txt")