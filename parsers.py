# Parsers to read predicates and rules from text files.
# Predicate "P(x,y)" is converted to ["P", "x", "y"]
# Rule "if P(x,y) then Q(z)" is converted to [["P", "x", "y"], ["Q", "z"]]


def _tokenize(line):
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


class BasicParser:
    def __init__(self):
        self.end_of_line = ""

    def _first_token(self):
        if len(self.tokens) > 0:
            self.i = 0
            self.token = self.tokens[self.i]
        else:
            self.token = self.end_of_line

    def _next_token(self):
        if len(self.tokens) > self.i + 1:
            self.i += 1
            self.token = self.tokens[self.i]
        else:
            self.token = self.end_of_line

    def _token_to_str(self, token):
        return token if token != self.end_of_line else "end-of-line"

    def _expect_token(self, expected):
        if self.token != expected:
            raise RuntimeError(f"'{self._token_to_str(expected)}' expected instead of '{self._token_to_str(self.token)}'")
        self._next_token()


class PredicateParser(BasicParser):
    def __init__(self):
        BasicParser.__init__(self)

    def _parse_predicate(self):
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
        return predicate
        
    
    def parse(self, line):
        self.tokens = _tokenize(line)
        self._first_token()
        if self.token in [self.end_of_line, "#"]:
            return None
        predicate = self._parse_predicate()
        self._expect_token(self.end_of_line)
        return predicate


def read_predicates(input_predicates_file):
    result = []
    parser = PredicateParser()
    with open(input_predicates_file, "r") as f:
        line_nr = 0
        for line in f:
            line_nr += 1
            try:
                predicate = parser.parse(line.strip())
                if predicate is not None:
                    result.append(predicate)
            except RuntimeError as e:
                print(f"{input_predicates_file}, line {line_nr}: {str(e)}")
    return result


def write_predicates(predicates, output_predicates_file):
    with open(output_predicates_file, "w") as f:
        for predicate in predicates:
            f.write(f"{predicate[0]}(" + ", ".join(predicate[1:]) + ")\n")


class RuleParser(PredicateParser):
    def __init__(self):
        PredicateParser.__init__(self)
        self.keywords = set(["if", "then", "and", "or"])

    def _parse_factor(self):
        '''the 'factor' in recursive descent expression parsing terminology'''
        if self.token == "(":
            self._next_token()
            result = self._parse_expression()
            self._expect_token(")")
        else:
            result = self._parse_predicate()
        return result

    def _parse_term(self):
        '''the 'term' in recursive descent expression parsing terminology'''
        result = self._parse_factor()
        if self.token == "and":
            result = ["and", result]
            while self.token == "and":
                self._next_token()
                result.append(self._parse_factor())
        return result

    def _parse_expression(self):
        '''the 'expression' in recursive descent expression parsing terminology'''
        result = self._parse_term()
        if self.token == "or":
            result = ["or", result]
            while self.token == "or":
                self._next_token()
                result.append(self._parse_term())
        return result

    def parse(self, line):
        self.tokens = _tokenize(line)
        self._first_token()
        if self.token in [self.end_of_line, "#"]:
            return None
        self._expect_token("if")
        cond = self._parse_expression()
        self._expect_token("then")
        predicate = self._parse_predicate()
        self._expect_token(self.end_of_line)
        return [cond, predicate]


def read_rules(rules_file):
    result = []
    parser = RuleParser()
    with open(rules_file, "r") as f:
        line_nr = 0
        for line in f:
            line_nr += 1
            try:
                rule = parser.parse(line.strip())
                if rule is not None:
                    result.append(rule)
            except RuntimeError as e:
                print(f"{rules_file}, line {line_nr}: {str(e)}")
                
    return result


if __name__ == "__main__":
    # a few simple tests
    predicates = read_predicates("input_predicates.txt")
    write_predicates(predicates, "output_predicates.txt")
    rules = read_rules("rules.txt")
    for rule in rules:      
        print(rule)
