import json
from json_scanner import Lexer, TokenType, Token

class LexerScanner:  # Grabs tokens from .txt files
    def __init__(self, file_path):
        self.file_path = file_path
        self.tokens = self.file_tokenization()
        self.current_index = 0

    def file_tokenization(self):
        tokens = []
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    token = self.create_token_from_line(line)
                    tokens.append(token)
        tokens.append(Token(TokenType.EOF))  # Ensure tokenization finishes
        return tokens
    
    def create_token_from_line(self, line):
        # Simple tokenization
        if line == '<{>':
            return Token(TokenType.LBRACE)
        elif line == '<}>':
            return Token(TokenType.RBRACE)
        elif line == '<[>':
            return Token(TokenType.LSQUARE)
        elif line == '<]>':
            return Token(TokenType.RSQUARE)
        elif line == '<:>':
            return Token(TokenType.COLON)
        elif line == '<,>':
            return Token(TokenType.COMMA)
        elif line == '<null>':
            return Token(TokenType.NULL)
        
        # More complex tokenization (bool, num, string)
        elif line.startswith('<str,'):
            content = line[5:-1].strip()  # Remove <str, and > 
            if content in ['true', 'false', 'null', '"true"', '"false"', '"null"']:
                raise Exception(f'Error type 4/7 at {content}: Cannot have boolean or null type in string.')
            if not content:
                raise Exception(f'Error type 2 at {content}: Cannot have empty strings.')
            return Token(TokenType.STRING, content)
        elif line.startswith('<num,'):
            content = line[5:-1].strip()
            if content.startswith('.') or content.endswith('.'):
                raise Exception(f"Error type 1 at {content}: Number cannot start or end with singular .")
            if content.startswith('+') or (content.startswith('0') and '.' not in content):
                raise Exception(f"Error type 3 at {content}: cannot start or end with 0, and cannot start with +.")
            return Token(TokenType.NUMBER, content)
        elif line.startswith('<bool,'):
            content = line[6:-1].strip()
            return Token(TokenType.BOOLEAN, content)
        else:
            raise Exception('Found invalid token.')

    def get_next_token(self):
        if self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            self.current_index += 1
            return token
        return Token(TokenType.EOF)

class Node:
    def __init__(self, label=None, is_leaf=False):
        self.label = label
        self.children = []
        self.is_leaf = is_leaf

    def add_child(self, child):
        self.children.append(child)

    def to_json_value(self):
        """
        Convert the Node tree into Python types that can be serialized into JSON.
        """
        # For leaf nodes, return the label directly
        if self.is_leaf:
            return self.label

        # For dictionary nodes (label == '{')
        if self.label == '{':
            obj = {}
            for child in self.children:
                # Each child represents a key-value pair.
                key = child.label
                obj[key] = child.children[0].to_json_value()
            return obj

        # For list nodes (label == '[')
        if self.label == '[':
            return [child.to_json_value() for child in self.children]

        return self.label

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.seen_keys = set()  # For duplicate key checking

    def get_next_token(self):
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.get_next_token()
        else:
            raise Exception(f"Expected token {token_type}, got {self.current_token.type}")
    
    def parse(self):
        self.get_next_token()
        return self.tree()
    
    def tree(self):
        node = self.subtree()
        if self.current_token.type != TokenType.EOF:
            raise Exception(f"Unexpected token {self.current_token.type} in end of input")
        return node
    
    def subtree(self):
        if self.current_token.type in {TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN, TokenType.NULL}:
            return self.leaf()
        elif self.current_token.type in {TokenType.LSQUARE, TokenType.LBRACE}:
            return self.internal_node()
        else:
            raise Exception(f"Unexpected token {self.current_token.type} in Subtree")
    
    def leaf(self):
        label = self.current_token.value
        if self.current_token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
        elif self.current_token.type == TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            label = True if label == "true" else False
        elif self.current_token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            label = float(label)
        elif self.current_token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            label = None
        else:
            raise Exception(f"Unexpected token {self.current_token.type} in Leaf")
        return Node(label=label, is_leaf=True)
    
    def internal_node(self):
        if self.current_token.type == TokenType.LBRACE:
            node = Node(label='{')
            self.eat(TokenType.LBRACE)
            while self.current_token.type != TokenType.RBRACE:
                key = self.current_token.value.strip('"')
                if key in self.seen_keys:
                    raise Exception(f"Error type 5 at {self.current_token.value}: Duplicate keys found.")
                self.seen_keys.add(key)
                self.eat(TokenType.STRING)
                self.eat(TokenType.COLON)
                value = self.subtree()
                child_node = Node(label=key)
                child_node.add_child(value)
                node.add_child(child_node)
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current_token.type in {TokenType.RBRACE, TokenType.EOF}:
                        raise Exception("Found extra comma when expected end of input.")
            self.eat(TokenType.RBRACE)
            return node
        
        elif self.current_token.type == TokenType.LSQUARE:
            node = Node(label='[')
            self.eat(TokenType.LSQUARE)
            current_type = None
            while self.current_token.type != TokenType.RSQUARE:
                value = self.subtree()
                if current_type is None:
                    current_type = type(value.label)
                else:
                    if type(value.label) != current_type:
                        raise Exception(f'Error type 6 at {value.label}: All elements in list must be the same type.')
                node.add_child(value)
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current_token.type in {TokenType.RSQUARE, TokenType.EOF}:
                        raise Exception("Found extra comma when expected end of input.")
            self.eat(TokenType.RSQUARE)
            return node

if __name__ == "__main__":
    for i in range(0, 10):
        input_file = f'test{i:02}.txt'  # e.g. test00.txt, test01.txt, etc.
        output_file = f'output{i:02}.json'  # Change file extension to .json

        try:
            lexer = LexerScanner(input_file)
            parser = Parser(lexer)
            tree = parser.parse()

            # Convert the tree into a valid JSON structure
            json_value = tree.to_json_value()
            with open(output_file, 'w') as output:
                json.dump(json_value, output, indent=2)

        except Exception as e:
            # Wrap the error message in a JSON object and write it to the output file
            with open(output_file, 'w') as output:
                error_obj = {"error": str(e)}
                json.dump(error_obj, output, indent=2)

    print('Parsing complete! Check output files for JSON outputs or errors.')
