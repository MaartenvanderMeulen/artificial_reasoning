def read_facts(input_facts_file):
    result = set()
    with open(input_facts_file, "r") as f:
        for line in f:
            result.add(line.strip())
    return result


def write_facts(facts, output_facts_file):
    facts = list(facts)
    facts.sort()
    with open(output_facts_file, "w") as f:
        for fact in facts:
            f.write(f"{fact}\n")


def _tokenize(line):
    return [token.lower() for token in line.replace("(", " ( ").replace(")", " ) ").split(" ") if token != '']


class LineParser:
    def __init__(self):
        self.keywords = set(["if", "then", "and", "or"])
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

    def _expect_token(self, expected):
        if self.token != expected:
            raise RuntimeError(f"'{expected}' expected instead of '{self.token}'")
        self._next_token()

    def _parse_fact(self):
        if not self.token.isidentifier() or self.token in self.keywords:
            raise RuntimeError(f"fact expected instead of '{self.token}'")
        fact = self.token
        self._next_token()
        return fact

    def _parse_end_of_line(self):
        if self.token != self.end_of_line:
            raise RuntimeError(f"end of line expected instead of '{self.token}'")

    def _parse_factor(self):
        if self.token == "(":
            self._next_token()
            result = self._parse_condition()
            self._expect_token(")")
        else:
            result = self._parse_fact()
        return result

    def _parse_and(self):
        result = self._parse_factor()
        if self.token == "and":
            result = ["and", result]
            while self.token == "and":
                self._next_token()
                result.append(self._parse_factor())
        return result

    def _parse_condition(self):
        result = self._parse_and()
        if self.token == "or":
            result = ["or", result]
            while self.token == "or":
                self._next_token()
                result.append(self._parse_and())
        return result

    def parse_line(self, line):
        self.tokens = _tokenize(line)
        self._first_token()
        self._expect_token("if")
        cond = self._parse_condition()
        self._expect_token("then")
        fact = self._parse_fact()
        self._expect_token(self.end_of_line)
        print(f"if {cond} then {fact}")
        return [cond, fact]


def read_rules(rules_file):
    result = []
    line_parser = LineParser()
    with open(rules_file, "r") as f:
        line_nr = 0
        for line in f:
            line_nr += 1
            try:
                result.append(line_parser.parse_line(line.strip()))
            except RuntimeError as e:
                print(f"{rules_file}, line {line_nr}: {str(e)}")
                
    return result
