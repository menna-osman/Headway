from abc import ABC, abstractmethod
import re


# Token types
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, POW, EOF, REGEX, STRING, COMMA = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')','^' ,'EOF','REGEX', 'STRING', ','
)

# Token mapping for operators
token_map = {
            '+': PLUS,
            '-': MINUS,
            '*': MUL,
            '/': DIV,
            '(': LPAREN,
            ')': RPAREN,
            '^': POW,
            ',': COMMA
        }
# Binary operations mapping
binary_operations = {
    PLUS: lambda x, y: x + y,
    MINUS: lambda x, y: x - y,
    MUL: lambda x, y: x * y,
    DIV: lambda x, y: x / y,
    POW: lambda x, y: x ** y
}


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class ICharacterReader(ABC):
    @abstractmethod
    def current_char(self):
        pass

    @abstractmethod
    def advance(self):
        pass


class ITokenizer(ABC):
    """Interface for converting characters into tokens"""
    @abstractmethod
    def tokenize(self, char: str):
        pass


class ILexicalAnalyzer(ABC):
    @abstractmethod
    def get_next_token(self) -> Token:
        pass


class TextReader(ICharacterReader):
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def current_char(self):
        if self.pos > len(self.text) - 1:
            return None
        return self.text[self.pos]

    def advance(self):
        self.pos += 1


class WhitespaceHandler:
    def __init__(self, reader: ICharacterReader):
        self.reader = reader

    def skip_whitespace(self):
        while self.reader.current_char() and self.reader.current_char().isspace():
            self.reader.advance()

class IntegerTokenizer(ITokenizer):
    def __init__(self, reader: ICharacterReader):
        self.reader = reader

    def tokenize(self, char):
        if not char.isdigit():
            return None

        result = ''
        while self.reader.current_char() and self.reader.current_char().isdigit():
            result += self.reader.current_char()
            self.reader.advance()
        return Token(INTEGER, int(result))



class OperatorTokenizer(ITokenizer):
    def __init__(self, token_map):
        self.token_map = token_map

    def tokenize(self, char: str):
        if char not in self.token_map:
            return None
        return Token(self.token_map[char], char)



class StringTokenizer(ITokenizer):
    def __init__(self, reader: ICharacterReader):
        self.reader = reader

    def tokenize(self, char):
        if char != '"':
            return None

        result = ''
        self.reader.advance()  # Skip opening quote

        while self.reader.current_char() and self.reader.current_char() != '"':
            result += self.reader.current_char()
            self.reader.advance()

        if self.reader.current_char() == '"':
            self.reader.advance()  # Skip closing quote
            return Token(STRING, result)

        raise Exception('Unterminated string')





class Lexer(ILexicalAnalyzer):
    def __init__(self, text, token_map):
        self.reader = TextReader(text)
        self.whitespace_handler = WhitespaceHandler(self.reader)
        self.tokenizers = [
            IntegerTokenizer(self.reader),
            OperatorTokenizer(token_map),
            StringTokenizer(self.reader),
        ]

    def error(self):
        raise Exception('Invalid character')

    def get_next_token(self):

        while self.reader.current_char() is not None:
            char = self.reader.current_char()
            if char.isspace():
                self.whitespace_handler.skip_whitespace()
                continue
            # Handle Regex keyword
            if char.lower() == 'r':
                text = ''
                while self.reader.current_char() and self.reader.current_char().isalpha():
                    text += self.reader.current_char()
                    self.reader.advance()
                if text.lower() == 'regex':
                    return Token(REGEX, 'REGEX')

            for tokenizer in self.tokenizers:
                if token := tokenizer.tokenize(char):
                    if tokenizer.__class__ != OperatorTokenizer:
                        return token
                    self.reader.advance()
                    return token

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class IParser(ABC):
    """Interface for parsing expressions"""
    @abstractmethod
    def parse(self):
        """Parses the input and returns AST"""
        pass

class RegexOp(AST):
    def __init__(self, text, pattern):
        self.text = text
        self.pattern = pattern

class String(AST):
    def __init__(self, value):
        self.value = value


class TokenReader:
    """Handles token reading and validation"""
    def __init__(self, lexer: ILexicalAnalyzer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()


class ExpressionParser:
    def __init__(self, token_reader: 'TokenReader'):
        self.token_reader = token_reader

    def factor(self):
        """factor : INTEGER | LPAREN expr RPAREN"""
        token = self.token_reader.current_token
        if token.type == INTEGER:
            self.token_reader.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.token_reader.eat(LPAREN)
            node = self.expr()
            self.token_reader.eat(RPAREN)
            return node
    def power(self):
        """
        power : factor POW factor
        """
        node = self.factor()
        while self.token_reader.current_token.type == POW:
            token = self.token_reader.current_token
            self.token_reader.eat(POW)

            node = BinOp(left=node, op=token, right=self.power())

        return node

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.power()

        while self.token_reader.current_token.type in (MUL, DIV):
            token = self.token_reader.current_token
            if token.type == MUL:
                self.token_reader.eat(MUL)
            elif token.type == DIV:
                self.token_reader.eat(DIV)

            node = BinOp(left=node, op=token, right=self.power())

        return node

    def expr(self):
        """
        expr   : regex_expr | term ((PLUS | MINUS) term)*
        term   : power ((MUL | DIV) power)*
        power  : factor (POW power)?
        factor : INTEGER | LPAREN expr RPAREN
        """
        if self.token_reader.current_token.type == REGEX:
            return self.regex_expr()
        node = self.term()

        while self.token_reader.current_token.type in (PLUS, MINUS):
            token = self.token_reader.current_token
            if token.type == PLUS:
                self.token_reader.eat(PLUS)
            elif token.type == MINUS:
                self.token_reader.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def regex_expr(self):
        """regex_expr : REGEX LPAREN STRING COMMA STRING RPAREN"""
        self.token_reader.eat(REGEX)
        self.token_reader.eat(LPAREN)
        text_token = self.token_reader.current_token
        self.token_reader.eat(STRING)
        self.token_reader.eat(COMMA)
        pattern_token = self.token_reader.current_token
        self.token_reader.eat(STRING)
        self.token_reader.eat(RPAREN)
        return RegexOp(text_token.value, pattern_token.value)
    


class Parser(IParser):
    """Main parser that coordinates parsing process"""
    def __init__(self, lexer: ILexicalAnalyzer):
        self.token_reader = TokenReader(lexer)
        self.expression_parser = ExpressionParser(self.token_reader)

    def parse(self):
        """Parses complete expression"""
        return self.expression_parser.expr()


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_RegexOp(self, node):
        pattern = node.pattern
        text = node.text
        try:
            match = re.search(pattern, text)
            return bool(match)
        except re.error as e:
            raise Exception(f"Invalid regex pattern: {str(e)}")

    def visit_BinOp(self, node):
        left= self.visit(node.left)
        right = self.visit(node.right)

        operation = binary_operations[node.op.type]
        return operation(left, right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


# def main():
#     while True:
#         try:
#             try:
#                 text = input('spi> ')
#             except NameError:  # Python3
#                 text = input('spi> ')
#         except EOFError:
#             break
#         if not text:
#             continue
#
#         lexer = Lexer(text)
#         parser = Parser(lexer)
#         interpreter = Interpreter(parser)
#         result = interpreter.interpret()
#         print(result)
#



