#Ben Strickland

class TokenType:

    LBRACE = 'LBRACE' # '{'
    RBRACE = 'RBRACE' # '}'
    LSQUARE = 'LSQUARE' # '['
    RSQUARE = 'RSQUARE' # ']'
    COMMA = 'COMMA' # ','
    COLON = 'COLON' # ':'
    QUOTATION = 'QUOTATION'
    STRING = 'STRING' # abcdef
    NUMBER = 'NUMBER' # 12345
    BOOLEAN = 'BOOLEAN' # false, true
    NULL = 'NULL' # null
    EOF = 'EOF' # End of input

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if(self.type == TokenType.LBRACE):
            return "<{>"
        elif(self.type == TokenType.RBRACE):
            return "<}>"
        elif(self.type == TokenType.LSQUARE):
            return "<[>"
        elif(self.type == TokenType.RSQUARE):
            return "<]>"
        elif(self.type == TokenType.COMMA):
            return "<,>"
        elif(self.type == TokenType.COLON):
            return "<:>"
        elif(self.type == TokenType.QUOTATION):
            return f'<str, {self.value}'
        elif(self.type == TokenType.STRING):
            return f'<str, {self.value}>'
        elif(self.type == TokenType.NUMBER):
            return f"<num, {self.value}>"
        elif(self.type == TokenType.BOOLEAN):
            return f"<bool, {self.value}>"
        elif(self.type == TokenType.NULL):
            return "<null>"
        else:
            return f"<{self.type}>"

# Lexer error
class LexerError(Exception):
    def __init__(self, position, character):
        self.position = position
        self.character = character
        super().__init__(f"Invalid character '{character}' at position {position}")
        
class Lexer:
    def __init__(self, input_text):
        # Input string
        self.input_text = input_text
        # Current position
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None
        # Symbol table
        self.symbol_table = {}

    # Input Buffering
    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            # End of input
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    # Skip whitespace
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Recognize string
    def recognize_string(self):
        result = ''
        if(self.current_char == '"'): # String recognizer can only start with a quotation mark
            result += self.current_char
            self.advance()
        else:
            raise LexerError(self.position, self.current_char)
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char.isspace()):
            if(self.current_char == '"'):
                break
            result += self.current_char
            self.advance()
        if(self.current_char == '"'): # Accept quotation mark
            result += self.current_char
            self.advance()
        else:
            raise LexerError(self.position, self.current_char)
        self.symbol_table[result] = 'STRING' # Store string in symbol table
        return Token(TokenType.STRING, result)
       
    # Recognize keyword
    def recognize_keyword(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum(): 
            result += self.current_char
            self.advance()
        if(result == 'true' or result == 'false'): # Checks if the token is a boolean
            self.symbol_table[result] = 'BOOLEAN'
            return Token(TokenType.BOOLEAN, result)
        elif(result == 'null'): # Checks if the token is null
            self.symbol_table[result] = 'NULL'
            return Token(TokenType.NULL, result)
        else:
            raise LexerError(self.position, self.current_char)
    
    # Recognize numbers
    def recognize_number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char in ['.',  '-', 'e'] and self.current_char != 0):
            if(self.current_char.isalpha() and self.current_char != 'e'):
                raise LexerError(self.position, self.current_char)
            result += self.current_char
            self.advance()
        if(self.current_char == 0): # Returns singular 0 if the entire token is zero
            self.symbol_table[result] = 'NUMBER'
            return Token(TokenType.NUMBER, float(0))
        self.symbol_table[result] = 'NUMBER'
        return Token(TokenType.NUMBER, float(result))
    
    # Get next token from input
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # All other tokens
            if(self.current_char == '{'):
                self.advance()
                return Token(TokenType.LBRACE)
            if(self.current_char == '}'):
                self.advance()
                return Token(TokenType.RBRACE)
            if(self.current_char == '['):
                self.advance()
                return Token(TokenType.LSQUARE)
            if(self.current_char == ']'):
                self.advance()
                return Token(TokenType.RSQUARE)
            if(self.current_char == ','):
                self.advance()
                return Token(TokenType.COMMA)
            if(self.current_char == '"'):
                return self.recognize_string()
            if(self.current_char == ':'):
                self.advance()
                return Token(TokenType.COLON)
            
            # Strings
            if self.current_char.isalpha() or self.current_char == '"':
                if(self.current_char in ['t', 'f', 'n']):
                    return self.recognize_keyword()
                return self.recognize_string()
            
            # Numbers 
            if self.current_char.isdigit() or self.current_char in ['-']:
                return self.recognize_number()
            # Unrecognized characters
            raise LexerError(self.position, self.current_char)
        # Eof
        return Token(TokenType.EOF)
    
    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        return tokens
            
# Testing the Lexer with input
if __name__ == "__main__":
    input_string = '{123 : "number"}'
    lexer = Lexer(input_string)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)