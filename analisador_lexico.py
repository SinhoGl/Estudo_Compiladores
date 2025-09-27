import re
from enum import Enum
from typing import List, Optional, NamedTuple

class TokenType(Enum):
    """Tipos de tokens que o analisador léxico pode reconhecer"""
    # Literais
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    
    # Palavras-chave
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    VAR = "VAR"
    
    # Operadores aritméticos
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    
    # Operadores de comparação
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # Operadores lógicos
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Atribuição
    ASSIGN = "ASSIGN"
    
    # Delimitadores
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    
    # Especiais
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

class Token(NamedTuple):
    """Representa um token encontrado no código fonte"""
    type: TokenType
    value: str
    line: int
    column: int

class LexicalError(Exception):
    """Exceção para erros léxicos"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro léxico na linha {line}, coluna {column}: {message}")

class Lexer:
    """Analisador léxico simples"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Palavras-chave da linguagem
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'var': TokenType.VAR,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT
        }
        
        # Operadores de um caractere
        self.single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET
        }
        
        # Operadores de dois caracteres
        self.double_char_tokens = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL
        }
    
    def current_char(self) -> Optional[str]:
        """Retorna o caractere atual ou None se chegou ao fim"""
        if self.position >= len(self.source_code):
            return None
        return self.source_code[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Olha para frente sem avançar a posição"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source_code):
            return None
        return self.source_code[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Avança para o próximo caractere"""
        if self.position >= len(self.source_code):
            return None
        
        char = self.source_code[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Pula espaços em branco (exceto quebras de linha)"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Pula comentários de linha (//)"""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Pula até o fim da linha
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> str:
        """Lê um número (inteiro ou decimal)"""
        number = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Segundo ponto, para de ler
                has_dot = True
            number += self.current_char()
            self.advance()
        
        return number
    
    def read_identifier(self) -> str:
        """Lê um identificador ou palavra-chave"""
        identifier = ''
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            identifier += self.current_char()
            self.advance()
        
        return identifier
    
    def read_string(self) -> str:
        """Lê uma string delimitada por aspas"""
        quote_char = self.current_char()  # ' ou "
        self.advance()  # Pula a aspa inicial
        
        string_value = ''
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                # Caractere de escape
                self.advance()
                if self.current_char():
                    escape_char = self.current_char()
                    if escape_char == 'n':
                        string_value += '\n'
                    elif escape_char == 't':
                        string_value += '\t'
                    elif escape_char == 'r':
                        string_value += '\r'
                    elif escape_char == '\\':
                        string_value += '\\'
                    elif escape_char == quote_char:
                        string_value += quote_char
                    else:
                        string_value += escape_char
                    self.advance()
            else:
                string_value += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise LexicalError("String não fechada", self.line, self.column)
        
        self.advance()  # Pula a aspa final
        return string_value
    
    def add_token(self, token_type: TokenType, value: str):
        """Adiciona um token à lista"""
        token = Token(token_type, value, self.line, self.column - len(value))
        self.tokens.append(token)
    
    def tokenize(self) -> List[Token]:
        """Realiza a análise léxica completa"""
        while self.current_char():
            # Pula espaços em branco
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Quebra de linha
            if self.current_char() == '\n':
                self.add_token(TokenType.NEWLINE, '\n')
                self.advance()
                continue
            
            # Comentários
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Números
            if self.current_char().isdigit():
                number = self.read_number()
                self.add_token(TokenType.NUMBER, number)
                continue
            
            # Strings
            if self.current_char() in '"\'':
                string_value = self.read_string()
                self.add_token(TokenType.STRING, string_value)
                continue
            
            # Identificadores e palavras-chave
            if self.current_char().isalpha() or self.current_char() == '_':
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier.lower(), TokenType.IDENTIFIER)
                self.add_token(token_type, identifier)
                continue
            
            # Operadores de dois caracteres
            two_char = self.current_char() + (self.peek_char() or '')
            if two_char in self.double_char_tokens:
                self.add_token(self.double_char_tokens[two_char], two_char)
                self.advance()
                self.advance()
                continue
            
            # Operadores de um caractere
            if self.current_char() in self.single_char_tokens:
                char = self.current_char()
                self.add_token(self.single_char_tokens[char], char)
                self.advance()
                continue
            
            # Caractere desconhecido
            unknown_char = self.current_char()
            self.advance()
            raise LexicalError(f"Caractere desconhecido: '{unknown_char}'", 
                             self.line, self.column - 1)
        
        # Adiciona token EOF
        self.add_token(TokenType.EOF, '')
        return self.tokens
    
    def print_tokens(self):
        """Imprime todos os tokens de forma formatada"""
        print(f"{'Tipo':<15} {'Valor':<15} {'Linha':<6} {'Coluna':<6}")
        print("-" * 50)
        
        for token in self.tokens:
            value_display = repr(token.value) if token.type == TokenType.STRING else token.value
            print(f"{token.type.value:<15} {value_display:<15} {token.line:<6} {token.column:<6}")


def main():
    """Função principal para demonstrar o uso do analisador léxico"""
    print("=== ANALISADOR LÉXICO SIMPLES ===")
    print("Este programa demonstra como funciona um analisador léxico.\n")
    
    # Exemplos de código para análise
    exemplos = [
        {
            "nome": "Exemplo 1: Expressão aritmética",
            "codigo": "x = 10 + 20 * 3.5"
        },
        {
            "nome": "Exemplo 2: Estrutura condicional",
            "codigo": """if (idade >= 18) {
    status = "adulto"
} else {
    status = "menor"
}"""
        },
        {
            "nome": "Exemplo 3: Função com loop",
            "codigo": """function calcular(n) {
    var resultado = 0
    for i = 1; i <= n; i = i + 1 {
        resultado = resultado + i
    }
    return resultado
}"""
        },
        {
            "nome": "Exemplo 4: Operadores lógicos e comparação",
            "codigo": """if (x > 0 and y != 0) or not z {
    // Este é um comentário
    print("Condição verdadeira")
}"""
        }
    ]
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"\n{'-'*60}")
        print(f"{exemplo['nome']}")
        print(f"{'-'*60}")
        print("Código fonte:")
        print(exemplo['codigo'])
        print("\nTokens encontrados:")
        
        try:
            lexer = Lexer(exemplo['codigo'])
            tokens = lexer.tokenize()
            lexer.print_tokens()
            
        except LexicalError as e:
            print(f"ERRO: {e}")
        
        if i < len(exemplos):
            input("\nPressione Enter para continuar...")
    
    print("\n" + "="*60)
    print("MODO INTERATIVO")
    print("Digite seu próprio código para análise (digite 'sair' para terminar):")
    print("="*60)
    
    while True:
        try:
            codigo = input("\n> ")
            if codigo.lower() in ['sair', 'exit', 'quit']:
                break
            
            if not codigo.strip():
                continue
            
            lexer = Lexer(codigo)
            tokens = lexer.tokenize()
            print("\nTokens:")
            lexer.print_tokens()
            
        except LexicalError as e:
            print(f"ERRO: {e}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nFim do analisador léxico!!")


if __name__ == "__main__":
    main()