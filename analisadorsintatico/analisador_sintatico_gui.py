#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANALISADOR SINTÁTICO PARA LINGUAGEM SIGMA

Trabalho de Compiladores - UESB 2025.2
Autores: Gleison Silva de Souza, Guilherme Oliveira Araujo
Professor: José Carlos Martins Oliveira

Este módulo implementa um analisador sintático completo para a linguagem Sigma-,
uma linguagem educacional do tipo Pascal simplificada. O analisador utiliza a
técnica de análise descendente recursiva (top-down parsing) e implementa uma
gramática livre de contexto com 14 não-terminais.

Gramática implementada:
S, D, V, T, I, L, C, A, R, W, F, G, M, N, P, E, B

Componentes principais:
- Analisador Léxico (Lexer): Converte código-fonte em tokens
- Analisador Sintático (Parser): Verifica conformidade com a gramática
- Interface Gráfica (GUI): Permite interação e visualização dos resultados
- Árvore Sintática (TreeNode): Representa estrutura hierárquica do programa

Tecnologias utilizadas:
- Python 3.12
- Tkinter para interface gráfica
- Enum para definição de tipos de tokens
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import Canvas
from enum import Enum
import os


class TokenType(Enum):
    """
    Enumeração dos tipos de tokens da linguagem Sigma-.
    
    Esta classe define todos os tipos possíveis de tokens que podem ser
    reconhecidos pelo analisador léxico. Cada token possui um valor string
    que representa sua categoria na linguagem.
    
    Categorias:
    - Literais: Valores diretos (números, identificadores, strings)
    - Palavras-chave: Reservadas da linguagem (program, var, if, etc.)
    - Operadores: Aritméticos, relacionais e de atribuição
    - Delimitadores: Símbolos que separam construções (;, ,, :, etc.)
    - Especiais: Controle interno (NEWLINE, EOF)
    """
    
    # =========================================================================
    # LITERAIS - Representam valores diretos no código
    # =========================================================================
    NUMBER = "num"          # Números inteiros (ex: 42, 100, -5)
    IDENTIFIER = "id"       # Identificadores/variáveis (ex: x, total, contador)
    STRING = "str"          # Strings literais (ex: "Hello", "Resultado: ")
    
    # =========================================================================
    # PALAVRAS-CHAVE - Reservadas da linguagem, não podem ser identificadores
    # =========================================================================
    PROGRAM = "program"     # Início da declaração do programa
    VAR = "var"            # Início da seção de declaração de variáveis
    INTEGER = "integer"     # Tipo de dados inteiro
    BOOLEAN = "boolean"     # Tipo de dados booleano
    BEGIN = "begin"        # Início de bloco de comandos
    END = "end"            # Fim de bloco de comandos
    READ = "read"          # Comando de leitura sem quebra de linha
    READLN = "readln"      # Comando de leitura com quebra de linha
    WRITE = "write"        # Comando de escrita sem quebra de linha
    WRITELN = "writeln"    # Comando de escrita com quebra de linha
    IF = "if"              # Início de estrutura condicional
    THEN = "then"          # Parte "então" do condicional
    ELSE = "else"          # Parte "senão" do condicional
    WHILE = "while"        # Início de estrutura de repetição
    DO = "do"              # Corpo do laço while
    
    # =========================================================================
    # OPERADORES ARITMÉTICOS - Realizam operações matemáticas
    # =========================================================================
    PLUS = "+"             # Adição
    MINUS = "-"            # Subtração ou negação unária
    MULTIPLY = "*"         # Multiplicação
    DIVIDE = "/"           # Divisão
    
    # =========================================================================
    # OPERADORES DE ATRIBUIÇÃO E RELACIONAIS - Comparação e atribuição
    # =========================================================================
    ASSIGN = ":="          # Atribuição (ex: x := 10)
    EQUAL = "="            # Igualdade (ex: x = 10)
    NOT_EQUAL = "<>"       # Diferente (ex: x <> 10)
    LESS_THAN = "<"        # Menor que (ex: x < 10)
    LESS_EQUAL = "<="      # Menor ou igual (ex: x <= 10)
    GREATER_THAN = ">"     # Maior que (ex: x > 10)
    GREATER_EQUAL = ">="   # Maior ou igual (ex: x >= 10)
    
    # =========================================================================
    # DELIMITADORES - Separam e estruturam o código
    # =========================================================================
    SEMICOLON = ";"        # Fim de comando ou declaração
    COMMA = ","            # Separador de elementos em listas
    COLON = ":"            # Separador em declarações (ex: x : integer)
    LEFT_PAREN = "("       # Parêntese esquerdo
    RIGHT_PAREN = ")"      # Parêntese direito
    DOT = "."              # Fim do programa
    
    # =========================================================================
    # ESPECIAIS - Controle interno do analisador
    # =========================================================================
    NEWLINE = "NEWLINE"    # Quebra de linha (removida na análise sintática)
    EOF = "EOF"            # Fim do arquivo (End Of File)


class Token:
    """
    Representa um token individual identificado no código-fonte.
    
    Um token é a menor unidade léxica significativa da linguagem. Cada token
    contém informações sobre seu tipo, valor e posição no código-fonte, o que
    é essencial para mensagens de erro precisas e análise sintática.
    
    Atributos:
        type (TokenType): Tipo do token (palavra-chave, operador, etc.)
        value (str): Valor literal do token como aparece no código
        line (int): Número da linha onde o token aparece (começa em 1)
        column (int): Número da coluna onde o token começa (começa em 1)
    
    Exemplo:
        Token(TokenType.NUMBER, "42", 3, 5)
        Representa o número 42 na linha 3, coluna 5
    """
    
    def __init__(self, token_type, value, line, column):
        """
        Inicializa um novo token.
        
        Args:
            token_type (TokenType): Tipo do token
            value (str): Valor literal do token
            line (int): Linha onde o token foi encontrado
            column (int): Coluna onde o token começa
        """
        self.type = token_type      # Tipo classificado do token
        self.value = value          # Texto original do token
        self.line = line            # Posição vertical no código
        self.column = column        # Posição horizontal no código

    def __repr__(self):
        """
        Representação string do token para debugging.
        
        Returns:
            str: Formato "Token(tipo, 'valor', linha:coluna)"
        """
        return f"Token({self.type.value}, {repr(self.value)}, {self.line}:{self.column})"


class LexicalError(Exception):
    """
    Exceção lançada quando um erro léxico é encontrado.
    
    Erros léxicos ocorrem quando o analisador encontra caracteres ou
    sequências que não são válidos na linguagem, como:
    - Caracteres não reconhecidos
    - Strings não terminadas
    - Comentários não fechados
    
    Atributos:
        message (str): Descrição do erro
        line (int): Linha onde o erro ocorreu
        column (int): Coluna onde o erro ocorreu
    """
    
    def __init__(self, message, line, column):
        """
        Inicializa uma exceção de erro léxico.
        
        Args:
            message (str): Descrição do erro
            line (int): Linha do erro
            column (int): Coluna do erro
        """
        self.message = message
        self.line = line
        self.column = column
        # Chama construtor da classe base com mensagem formatada
        super().__init__(f"Erro léxico na linha {line}, coluna {column}: {message}")


class SyntaxError(Exception):
    """
    Exceção lançada quando um erro sintático é encontrado.
    
    Erros sintáticos ocorrem quando a sequência de tokens não está de acordo
    com a gramática da linguagem, como:
    - Token inesperado (ex: esperava-se ';' mas encontrou 'end')
    - Estrutura incompleta (ex: if sem then)
    - Ordem incorreta de elementos
    
    Atributos:
        message (str): Descrição do erro
        token (Token): Token que causou o erro (opcional)
    """
    
    def __init__(self, message, token=None):
        """
        Inicializa uma exceção de erro sintático.
        
        Args:
            message (str): Descrição do erro
            token (Token, opcional): Token problemático para contexto adicional
        """
        self.message = message
        self.token = token
        
        # Se houver token, inclui informações de contexto na mensagem
        if token:
            super().__init__(
                f"Erro sintático: {message} "
                f"(Token: {token.type.value}, Linha: {token.line})"
            )
        else:
            super().__init__(f"Erro sintático: {message}")


class TreeNode:
    """
    Nó da árvore sintática de derivação.
    
    A árvore sintática representa a estrutura hierárquica do programa analisado.
    Cada nó pode ser:
    - Terminal: Representa um token do código (folha da árvore)
    - Não-terminal: Representa uma construção gramatical (nó interno)
    
    A árvore é construída durante a análise sintática e pode ser visualizada
    de forma hierárquica usando caracteres especiais (├──, └──, │).
    
    Atributos:
        symbol (str): Símbolo gramatical (S, D, V, etc.) ou terminal
        token (Token): Token associado (None para não-terminais)
        children (list): Lista de nós filhos
    
    Exemplo de árvore:
        S
         ├── program → "program"
         ├── id → "exemplo"
         └── ;  → ";"
    """
    
    def __init__(self, symbol, token=None, children=None):
        """
        Inicializa um nó da árvore sintática.
        
        Args:
            symbol (str): Símbolo gramatical ou nome do terminal
            token (Token, opcional): Token associado se for terminal
            children (list, opcional): Lista inicial de filhos
        """
        self.symbol = symbol      # Símbolo da gramática (ex: "S", "id", "+")
        self.token = token        # Token real (apenas para terminais)
        self.children = children if children else []  # Filhos do nó
    
    def add_child(self, child):
        """
        Adiciona um filho ao nó.
        
        Args:
            child (TreeNode): Nó filho a ser adicionado
        
        Returns:
            TreeNode: Retorna self para permitir encadeamento
        """
        self.children.append(child)
        return self  # Permite: node.add_child(child1).add_child(child2)
    
    def __repr__(self):
        """
        Representação compacta do nó para debugging.
        
        Returns:
            str: "Símbolo" ou "Símbolo(valor)" para terminais
        """
        if self.token:
            return f"{self.symbol}({self.token.value})"
        return self.symbol
    
    def to_string(self, level=0, is_last=True, prefix=""):
        """
        Gera representação hierárquica da árvore em formato texto.
        
        Utiliza caracteres especiais para desenhar a estrutura:
        - ├── para filhos intermediários
        - └── para último filho
        - │   para linhas verticais de conexão
        - →   para separar símbolo de valor (terminais)
        
        Args:
            level (int): Nível de profundidade atual (0 = raiz)
            is_last (bool): Se este nó é o último filho do pai
            prefix (str): Prefixo acumulado para indentação
        
        Returns:
            str: Representação hierárquica da árvore
        
        Exemplo de saída:
            S
             ├── program → "program"
             ├── id → "exemplo"
             ├── ; → ";"
             ├── D
             │    ├── var → "var"
             │    └── V
             └── begin → "begin"
        """
        result = ""
        
        # =====================================================================
        # Desenha o nó atual
        # =====================================================================
        if level == 0:
            # Raiz da árvore: sem prefixo ou conector
            result += f"{self.symbol}\n"
        else:
            # Escolhe conector apropriado
            connector = "└── " if is_last else "├── "
            
            if self.token:
                # Terminal: mostra símbolo → "valor"
                result += f"{prefix}{connector}{self.symbol} → \"{self.token.value}\"\n"
            else:
                # Não-terminal: apenas símbolo
                result += f"{prefix}{connector}{self.symbol}\n"
        
        # =====================================================================
        # Desenha os filhos recursivamente
        # =====================================================================
        for i, child in enumerate(self.children):
            # Verifica se é o último filho
            is_last_child = (i == len(self.children) - 1)
            
            # Calcula extensão do prefixo para os filhos
            if level == 0:
                # Filhos da raiz não têm prefixo
                extension = ""
            else:
                # Se pai não é o último, adiciona linha vertical
                # Se pai é o último, adiciona espaços
                extension = "    " if is_last else "│   "
            
            # Chama recursivamente para cada filho
            result += child.to_string(
                level + 1,              # Incrementa profundidade
                is_last_child,          # Passa status de último filho
                prefix + extension      # Acumula prefixo
            )
        
        return result


class Lexer:
    """
    Analisador Léxico (Scanner) para a linguagem Sigma-.
    
    O Lexer é responsável pela primeira fase da compilação: transformar o
    código-fonte (string) em uma sequência de tokens. Ele:
    
    1. Percorre o código caractere por caractere
    2. Reconhece padrões léxicos (palavras-chave, números, operadores, etc.)
    3. Gera tokens com informações de tipo, valor e posição
    4. Ignora espaços em branco e comentários
    5. Detecta erros léxicos (caracteres inválidos, strings não terminadas)
    
    Características:
    - Reconhece 15 palavras-chave
    - Suporta operadores de 1 e 2 caracteres
    - Trata comentários delimitados por chaves { }
    - Mantém rastreamento de linha e coluna para erros precisos
    
    Exemplo de uso:
        lexer = Lexer("program exemplo; begin end.")
        tokens = lexer.tokenize()
    """
    
    def __init__(self, source_code):
        """
        Inicializa o analisador léxico com o código-fonte.
        
        Args:
            source_code (str): Código-fonte completo a ser analisado
        """
        # Código-fonte a ser analisado
        self.source = source_code
        
        # Lista de tokens gerados
        self.tokens = []
        
        # Posição atual no código (índice do caractere)
        self.current = 0
        
        # Linha atual (começa em 1)
        self.line = 1
        
        # Coluna atual (começa em 1)
        self.column = 1

        # =====================================================================
        # Tabela de palavras-chave da linguagem
        # =====================================================================
        # Mapeia palavras reservadas (minúsculas) para seus tipos de token
        # Importante: As comparações são case-insensitive
        self.keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'integer': TokenType.INTEGER,
            'boolean': TokenType.BOOLEAN,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'read': TokenType.READ,
            'readln': TokenType.READLN,
            'write': TokenType.WRITE,
            'writeln': TokenType.WRITELN,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
        }

        # =====================================================================
        # Tabela de operadores e delimitadores de um caractere
        # =====================================================================
        self.single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.EQUAL,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '.': TokenType.DOT,
        }

        # =====================================================================
        # Tabela de operadores de dois caracteres
        # =====================================================================
        # Estes devem ser verificados ANTES dos de um caractere
        # para evitar reconhecimento incorreto (ex: := vs : e =)
        self.double_char_tokens = {
            ':=': TokenType.ASSIGN,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '<>': TokenType.NOT_EQUAL,
        }

    def is_at_end(self):
        """
        Verifica se chegamos ao fim do código-fonte.
        
        Returns:
            bool: True se não há mais caracteres para processar
        """
        return self.current >= len(self.source)

    def advance(self):
        """
        Consome e retorna o caractere atual, avançando a posição.
        
        Também mantém rastreamento de linha e coluna:
        - Incrementa linha e reseta coluna ao encontrar \n
        - Incrementa coluna para outros caracteres
        
        Returns:
            str: Caractere atual ou '\0' se fim do arquivo
        """
        if not self.is_at_end():
            ch = self.source[self.current]  # Pega caractere atual
            self.current += 1                # Avança posição
            
            # Atualiza rastreamento de linha/coluna
            if ch == '\n':
                self.line += 1      # Nova linha
                self.column = 1     # Reseta coluna
            else:
                self.column += 1    # Avança coluna
            
            return ch
        
        # Retorna '\0' para indicar fim do arquivo
        return '\0'

    def peek(self):
        """
        Visualiza o caractere atual sem consumi-lo.
        
        Returns:
            str: Caractere atual ou '\0' se fim do arquivo
        """
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        """
        Visualiza o próximo caractere sem consumi-lo.
        
        Útil para reconhecer operadores de dois caracteres.
        
        Returns:
            str: Próximo caractere ou '\0' se não houver
        """
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def add_token(self, token_type, value):
        """
        Cria e adiciona um token à lista de tokens.
        
        Args:
            token_type (TokenType): Tipo do token
            value (str): Valor literal do token
        
        Note:
            A coluna é ajustada subtraindo o comprimento do token
            para apontar para o início dele, não o fim
        """
        token = Token(
            token_type,
            value,
            self.line,
            self.column - len(str(value))  # Aponta para início do token
        )
        self.tokens.append(token)

    def scan_string(self):
        """
        Escaneia uma string literal delimitada por aspas duplas.
        
        Começa após a aspa inicial já ter sido consumida e continua
        até encontrar a aspa final. Suporta strings multi-linha.
        
        Returns:
            str: Conteúdo da string (sem as aspas)
        
        Raises:
            LexicalError: Se a string não for terminada antes do fim do arquivo
        """
        value = ""
        
        # Continua até encontrar aspa final ou fim do arquivo
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                # Strings podem conter quebras de linha
                self.line += 1
                self.column = 1
            value += self.advance()
        
        # Verifica se string foi terminada
        if self.is_at_end():
            raise LexicalError("String não terminada", self.line, self.column)
        
        # Consome aspa final
        self.advance()
        
        return value

    def scan_number(self):
        """
        Escaneia um número inteiro.
        
        Continua consumindo dígitos até encontrar um caractere
        não-numérico. Não suporta ponto decimal (apenas inteiros).
        
        Returns:
            str: String contendo o número
        """
        value = ""
        
        # Consome todos os dígitos consecutivos
        while self.peek().isdigit():
            value += self.advance()
        
        return value

    def scan_identifier(self):
        """
        Escaneia um identificador ou palavra-chave.
        
        Identificadores começam com letra ou underscore e podem
        conter letras, dígitos e underscores. Após escaneado,
        o valor é verificado contra a tabela de palavras-chave.
        
        Returns:
            str: String contendo o identificador
        """
        value = ""
        
        # Consome caracteres alfanuméricos e underscore
        while self.peek().isalnum() or self.peek() == '_':
            value += self.advance()
        
        return value

    def tokenize(self):
        """
        Realiza a análise léxica completa do código-fonte.
        
        Este é o método principal do Lexer. Percorre todo o código,
        reconhecendo e classificando cada elemento léxico. O processo:
        
        1. Ignora espaços em branco (' ', \t, \r)
        2. Trata quebras de linha (\n)
        3. Ignora comentários ({ ... })
        4. Reconhece strings ("...")
        5. Reconhece números (sequências de dígitos)
        6. Reconhece identificadores e palavras-chave
        7. Reconhece operadores de dois caracteres (:=, <=, etc.)
        8. Reconhece operadores de um caractere (+, -, etc.)
        9. Lança erro para caracteres desconhecidos
        
        Returns:
            list[Token]: Lista de tokens reconhecidos (inclui EOF no final)
        
        Raises:
            LexicalError: Se encontrar caractere inválido ou erro léxico
        """
        # Reinicializa estado para nova análise
        self.tokens = []
        self.current = 0
        self.line = 1
        self.column = 1

        # =====================================================================
        # Loop principal: processa cada caractere do código
        # =====================================================================
        while not self.is_at_end():
            ch = self.peek()  # Olha caractere atual

            # =================================================================
            # 1. Ignora espaços em branco
            # =================================================================
            if ch in ' \t\r':
                self.advance()  # Consome e ignora
                continue

            # =================================================================
            # 2. Trata quebra de linha
            # =================================================================
            if ch == '\n':
                # Adiciona token NEWLINE (removido depois pelo parser)
                self.add_token(TokenType.NEWLINE, '\\n')
                self.advance()
                continue

            # =================================================================
            # 3. Trata comentários { ... }
            # =================================================================
            if ch == '{':
                self.advance()  # Consome '{'
                
                # Pula até encontrar '}' ou fim do arquivo
                while self.peek() != '}' and not self.is_at_end():
                    self.advance()
                
                # Verifica se comentário foi fechado
                if self.is_at_end():
                    raise LexicalError(
                        "Comentário não terminado",
                        self.line,
                        self.column
                    )
                
                self.advance()  # Consome '}'
                continue

            # =================================================================
            # 4. Trata strings "..."
            # =================================================================
            if ch == '"':
                self.advance()  # Consome '"' inicial
                string_value = self.scan_string()  # Escaneia conteúdo
                self.add_token(TokenType.STRING, string_value)
                continue

            # =================================================================
            # 5. Trata números (inteiros)
            # =================================================================
            if ch.isdigit():
                num_value = self.scan_number()
                self.add_token(TokenType.NUMBER, num_value)
                continue

            # =================================================================
            # 6. Trata identificadores e palavras-chave
            # =================================================================
            if ch.isalpha() or ch == '_':
                ident = self.scan_identifier()
                
                # Verifica se é palavra-chave (case-insensitive)
                lower_ident = ident.lower()
                token_type = self.keywords.get(lower_ident, TokenType.IDENTIFIER)
                
                self.add_token(token_type, ident)
                continue

            # =================================================================
            # 7. Trata operadores de dois caracteres (:=, <=, >=, <>)
            # =================================================================
            # IMPORTANTE: Deve vir ANTES dos de um caractere
            two = ch + self.peek_next()
            if two in self.double_char_tokens:
                self.advance()  # Consome primeiro caractere
                self.advance()  # Consome segundo caractere
                self.add_token(self.double_char_tokens[two], two)
                continue

            # =================================================================
            # 8. Trata operadores e delimitadores de um caractere
            # =================================================================
            if ch in self.single_char_tokens:
                self.advance()
                self.add_token(self.single_char_tokens[ch], ch)
                continue

            # =================================================================
            # 9. Caractere desconhecido - ERRO LÉXICO
            # =================================================================
            unknown = self.advance()
            raise LexicalError(
                f"Caractere desconhecido: '{unknown}'",
                self.line,
                self.column - 1
            )

        # =====================================================================
        # Adiciona token de fim de arquivo (EOF)
        # =====================================================================
        self.add_token(TokenType.EOF, '')
        
        return self.tokens


class Parser:
    """
    Analisador Sintático Descendente Recursivo para Sigma-.
    
    O Parser é responsável pela segunda fase da compilação: verificar se a
    sequência de tokens está de acordo com a gramática da linguagem e construir
    a árvore sintática correspondente.
    
    Técnica utilizada: Análise Descendente Recursiva
    - Cada não-terminal da gramática é implementado como um método
    - Cada método constrói um nó da árvore sintática
    - A análise parte do símbolo inicial (S) e desce recursivamente
    
    Gramática Sigma- (14 não-terminais):
    
    S -> program id; D begin L end. | program id; begin L end.
    D -> var V
    V -> I: T; V | I : T;
    T -> integer | boolean
    I -> id | id,I
    L -> C; | C;L
    C -> A | R | W | M | N | P
    A -> id := E
    R -> read(I) | readln | readln(I)
    W -> write(F) | writeln | writeln(F)
    F -> G | G,F
    G -> str | E
    M -> begin L end
    N -> if B then C | if B then C else C
    P -> while B do C
    E -> E + E | E - E | E * E | E / E | - E | (E) | id | num
    B -> E < E | E <= E | E > E | E >= E | E = E | E <> E | id
    
    Note que as produções de E foram transformadas para eliminar
    recursão à esquerda e implementar precedência de operadores.
    """
    
    def __init__(self, tokens):
        """
        Inicializa o analisador sintático com a lista de tokens.
        
        Args:
            tokens (list[Token]): Lista de tokens do analisador léxico
        """
        # Remove tokens NEWLINE e EOF iniciais
        # NEWLINE não é relevante para sintaxe
        self.tokens = [
            t for t in tokens
            if t.type != TokenType.NEWLINE and t.type != TokenType.EOF
        ]
        
        # Adiciona EOF no final para marcar fim da entrada
        self.tokens.append(Token(TokenType.EOF, '$', -1, -1))
        
        # Índice do token atual sendo analisado
        self.current = 0
    
    def peek(self):
        """
        Visualiza o token atual sem consumi-lo.
        
        Returns:
            Token: Token atual ou EOF se além do fim
        """
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF
    
    def advance(self):
        """
        Consome e retorna o token atual, avançando para o próximo.
        
        Returns:
            Token: Token que foi consumido
        """
        token = self.peek()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def expect(self, token_type):
        """
        Verifica se o token atual é do tipo esperado e o consome.
        
        Este é o método fundamental da análise sintática descendente.
        Se o token não for do tipo esperado, lança erro sintático.
        
        Args:
            token_type (TokenType): Tipo esperado do token
        
        Returns:
            Token: Token consumido
        
        Raises:
            SyntaxError: Se token atual não for do tipo esperado
        """
        token = self.peek()
        
        # Verifica se tipo do token atual bate com o esperado
        if token.type != token_type:
            raise SyntaxError(
                f"Esperado '{token_type.value}', "
                f"encontrado '{token.type.value}'",
                token
            )
        
        # Token correto: consome e retorna
        return self.advance()
    
    def parse(self):
        """
        Inicia a análise sintática completa.
        
        Este é o ponto de entrada principal do parser. Chama o método
        correspondente ao símbolo inicial da gramática (S) e verifica
        se todos os tokens foram consumidos.
        
        Returns:
            TreeNode: Raiz da árvore sintática
        
        Raises:
            SyntaxError: Se houver erro na análise
        """
        try:
            # Começa pela raiz da gramática (S -> Programa)
            tree = self.parse_S()
            
            # Verifica se todos os tokens foram consumidos
            if self.peek().type != TokenType.EOF:
                raise SyntaxError("Esperado fim do programa", self.peek())
            
            return tree
            
        except SyntaxError as e:
            # Repropaga erro sintático
            raise e
    
    # =========================================================================
    # MÉTODOS DE PARSING - Um para cada não-terminal da gramática
    # =========================================================================
    
    def parse_S(self):
        """
        S -> program id; D begin L end. | program id; begin L end.
        
        Parseia um programa completo. Um programa Sigma- tem a estrutura:
        1. Palavra-chave 'program'
        2. Identificador (nome do programa)
        3. Ponto-e-vírgula
        4. Declarações (opcional - D)
        5. begin
        6. Lista de comandos (L)
        7. end
        8. Ponto final
        
        Returns:
            TreeNode: Nó raiz representando o programa completo
        """
        node = TreeNode("S")  # S = Programa
        
        # 1. Espera 'program'
        prog_token = self.expect(TokenType.PROGRAM)
        node.add_child(TreeNode("program", token=prog_token))
        
        # 2. Espera identificador (nome do programa)
        id_token = self.expect(TokenType.IDENTIFIER)
        node.add_child(TreeNode("id", token=id_token))
        
        # 3. Espera ponto-e-vírgula
        semi_token = self.expect(TokenType.SEMICOLON)
        node.add_child(TreeNode(";", token=semi_token))
        
        # 4. Declarações (opcional) - verifica se tem 'var'
        if self.peek().type == TokenType.VAR:
            node.add_child(self.parse_D())
        
        # 5. Espera 'begin'
        begin_token = self.expect(TokenType.BEGIN)
        node.add_child(TreeNode("begin", token=begin_token))
        
        # 6. Lista de comandos
        node.add_child(self.parse_L())
        
        # 7. Espera 'end'
        end_token = self.expect(TokenType.END)
        node.add_child(TreeNode("end", token=end_token))
        
        # 8. Espera ponto final
        dot_token = self.expect(TokenType.DOT)
        node.add_child(TreeNode(".", token=dot_token))
        
        return node
    
    def parse_D(self):
        """
        D -> var V
        
        Parseia a seção de declarações de variáveis.
        Começa com 'var' seguido de uma ou mais declarações (V).
        
        Returns:
            TreeNode: Nó representando as declarações
        """
        node = TreeNode("D")  # D = Declarações
        
        # Espera 'var'
        var_token = self.expect(TokenType.VAR)
        node.add_child(TreeNode("var", token=var_token))
        
        # Lista de variáveis
        node.add_child(self.parse_V())
        
        return node
    
    def parse_V(self):
        """
        V -> I: T; V | I : T;
        
        Parseia uma ou mais declarações de variáveis.
        Formato: identificador(es) : tipo;
        Exemplo: x, y : integer;
        
        Recursão: permite múltiplas declarações consecutivas.
        
        Returns:
            TreeNode: Nó representando lista de variáveis
        """
        node = TreeNode("V")  # V = Lista de variáveis
        
        # Lista de identificadores (ex: x, y, z)
        node.add_child(self.parse_I())
        
        # Dois-pontos
        colon_token = self.expect(TokenType.COLON)
        node.add_child(TreeNode(":", token=colon_token))
        
        # Tipo (integer ou boolean)
        node.add_child(self.parse_T())
        
        # Ponto-e-vírgula
        semi_token = self.expect(TokenType.SEMICOLON)
        node.add_child(TreeNode(";", token=semi_token))
        
        # Se próximo token é identificador, há mais declarações
        if self.peek().type == TokenType.IDENTIFIER:
            node.add_child(self.parse_V())  # Recursão
        
        return node
    
    def parse_T(self):
        """
        T -> integer | boolean
        
        Parseia um tipo de dados.
        Sigma- suporta apenas dois tipos: integer e boolean.
        
        Returns:
            TreeNode: Nó representando o tipo
        
        Raises:
            SyntaxError: Se não for 'integer' nem 'boolean'
        """
        token = self.peek()
        
        if token.type == TokenType.INTEGER:
            self.advance()
            return TreeNode("T").add_child(TreeNode("integer", token=token))
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return TreeNode("T").add_child(TreeNode("boolean", token=token))
        else:
            raise SyntaxError("Esperado tipo (integer ou boolean)", token)
    
    def parse_I(self):
        """
        I -> id | id,I
        
        Parseia uma lista de identificadores separados por vírgula.
        Exemplo: x, y, z
        
        Recursão: permite lista arbitrariamente longa.
        
        Returns:
            TreeNode: Nó representando lista de IDs
        """
        node = TreeNode("I")  # I = Lista de identificadores
        
        # Identificador obrigatório
        id_token = self.expect(TokenType.IDENTIFIER)
        node.add_child(TreeNode("id", token=id_token))
        
        # Se há vírgula, há mais identificadores
        if self.peek().type == TokenType.COMMA:
            comma_token = self.advance()
            node.add_child(TreeNode(",", token=comma_token))
            node.add_child(self.parse_I())  # Recursão
        
        return node
    
    def parse_L(self):
        """
        L -> C; | C;L
        
        Parseia uma lista de comandos separados por ponto-e-vírgula.
        Exemplo:
            x := 10;
            y := 20;
            writeln(x)
        
        Recursão: permite lista arbitrariamente longa.
        
        Returns:
            TreeNode: Nó representando lista de comandos
        """
        node = TreeNode("L")  # L = Lista de comandos
        
        # Comando obrigatório
        node.add_child(self.parse_C())
        
        # Se há ponto-e-vírgula, pode haver mais comandos
        if self.peek().type == TokenType.SEMICOLON:
            semi_token = self.advance()
            node.add_child(TreeNode(";", token=semi_token))
            
            # Se não é 'end' nem EOF, há mais comandos
            if self.peek().type not in [TokenType.END, TokenType.EOF]:
                node.add_child(self.parse_L())  # Recursão
        
        return node
    
    def parse_C(self):
        """
        C -> A | R | W | M | N | P
        
        Parseia um comando. Comando pode ser:
        - A: Atribuição (id := E)
        - R: Leitura (read/readln)
        - W: Escrita (write/writeln)
        - M: Bloco composto (begin...end)
        - N: Condicional (if...then...else)
        - P: Repetição (while...do)
        
        Usa o primeiro token para decidir qual tipo de comando é.
        
        Returns:
            TreeNode: Nó representando o comando
        
        Raises:
            SyntaxError: Se token não inicia nenhum comando válido
        """
        node = TreeNode("C")  # C = Comando
        token = self.peek()
        
        # Decide tipo do comando baseado no token atual
        if token.type == TokenType.IDENTIFIER:
            # Identificador -> Atribuição
            node.add_child(self.parse_A())
            
        elif token.type in [TokenType.READ, TokenType.READLN]:
            # read ou readln -> Leitura
            node.add_child(self.parse_R())
            
        elif token.type in [TokenType.WRITE, TokenType.WRITELN]:
            # write ou writeln -> Escrita
            node.add_child(self.parse_W())
            
        elif token.type == TokenType.BEGIN:
            # begin -> Bloco composto
            node.add_child(self.parse_M())
            
        elif token.type == TokenType.IF:
            # if -> Condicional
            node.add_child(self.parse_N())
            
        elif token.type == TokenType.WHILE:
            # while -> Repetição
            node.add_child(self.parse_P())
            
        else:
            # Token não inicia nenhum comando válido
            raise SyntaxError(f"Comando inválido", token)
        
        return node
    
    def parse_A(self):
        """
        A -> id := E
        
        Parseia uma atribuição.
        Formato: identificador := expressão
        Exemplo: x := 10 + y
        
        Returns:
            TreeNode: Nó representando a atribuição
        """
        node = TreeNode("A")  # A = Atribuição
        
        # Identificador (variável recebendo valor)
        id_token = self.expect(TokenType.IDENTIFIER)
        node.add_child(TreeNode("id", token=id_token))
        
        # Operador de atribuição ':='
        assign_token = self.expect(TokenType.ASSIGN)
        node.add_child(TreeNode(":=", token=assign_token))
        
        # Expressão (valor a ser atribuído)
        node.add_child(self.parse_E())
        
        return node
    
    def parse_R(self):
        """
        R -> read(I) | readln | readln(I)
        
        Parseia um comando de leitura. Pode ser:
        - read(var): lê sem pular linha
        - readln: pula linha
        - readln(var): lê e pula linha
        
        Returns:
            TreeNode: Nó representando a leitura
        """
        node = TreeNode("R")  # R = Leitura
        token = self.peek()
        
        if token.type == TokenType.READ:
            # read(I) - obrigatório ter parênteses e identificadores
            read_token = self.advance()
            node.add_child(TreeNode("read", token=read_token))
            
            lparen_token = self.expect(TokenType.LEFT_PAREN)
            node.add_child(TreeNode("(", token=lparen_token))
            
            node.add_child(self.parse_I())  # Lista de variáveis
            
            rparen_token = self.expect(TokenType.RIGHT_PAREN)
            node.add_child(TreeNode(")", token=rparen_token))
            
        elif token.type == TokenType.READLN:
            # readln ou readln(I) - parênteses opcionais
            readln_token = self.advance()
            node.add_child(TreeNode("readln", token=readln_token))
            
            # Se tem parêntese, lê lista de variáveis
            if self.peek().type == TokenType.LEFT_PAREN:
                lparen_token = self.advance()
                node.add_child(TreeNode("(", token=lparen_token))
                
                node.add_child(self.parse_I())
                
                rparen_token = self.expect(TokenType.RIGHT_PAREN)
                node.add_child(TreeNode(")", token=rparen_token))
        
        return node
    
    def parse_W(self):
        """
        W -> write(F) | writeln | writeln(F)
        
        Parseia um comando de escrita. Pode ser:
        - write(lista): escreve sem pular linha
        - writeln: pula linha
        - writeln(lista): escreve e pula linha
        
        Returns:
            TreeNode: Nó representando a escrita
        """
        node = TreeNode("W")  # W = Escrita
        token = self.peek()
        
        if token.type == TokenType.WRITE:
            # write(F) - obrigatório ter parênteses e lista
            write_token = self.advance()
            node.add_child(TreeNode("write", token=write_token))
            
            lparen_token = self.expect(TokenType.LEFT_PAREN)
            node.add_child(TreeNode("(", token=lparen_token))
            
            node.add_child(self.parse_F())  # Lista de saída
            
            rparen_token = self.expect(TokenType.RIGHT_PAREN)
            node.add_child(TreeNode(")", token=rparen_token))
            
        elif token.type == TokenType.WRITELN:
            # writeln ou writeln(F) - parênteses opcionais
            writeln_token = self.advance()
            node.add_child(TreeNode("writeln", token=writeln_token))
            
            # Se tem parêntese, lê lista de saída
            if self.peek().type == TokenType.LEFT_PAREN:
                lparen_token = self.advance()
                node.add_child(TreeNode("(", token=lparen_token))
                
                node.add_child(self.parse_F())
                
                rparen_token = self.expect(TokenType.RIGHT_PAREN)
                node.add_child(TreeNode(")", token=rparen_token))
        
        return node
    
    def parse_F(self):
        """
        F -> G | G,F
        
        Parseia lista de saída (para write/writeln).
        Lista pode conter strings e expressões misturadas.
        Exemplo: "Resultado: ", x, " = ", y
        
        Returns:
            TreeNode: Nó representando lista de saída
        """
        node = TreeNode("F")  # F = Lista de saída
        
        # Item de saída obrigatório
        node.add_child(self.parse_G())
        
        # Se há vírgula, há mais itens
        if self.peek().type == TokenType.COMMA:
            comma_token = self.advance()
            node.add_child(TreeNode(",", token=comma_token))
            node.add_child(self.parse_F())  # Recursão
        
        return node
    
    def parse_G(self):
        """
        G -> str | E
        
        Parseia um item de saída. Pode ser:
        - String literal ("texto")
        - Expressão (variável ou cálculo)
        
        Returns:
            TreeNode: Nó representando item de saída
        """
        node = TreeNode("G")  # G = Item de saída
        
        if self.peek().type == TokenType.STRING:
            # String literal
            str_token = self.advance()
            node.add_child(TreeNode("str", token=str_token))
        else:
            # Expressão
            node.add_child(self.parse_E())
        
        return node
    
    def parse_M(self):
        """
        M -> begin L end
        
        Parseia um bloco composto (vários comandos agrupados).
        Permite agrupar múltiplos comandos onde sintaxe espera um.
        
        Exemplo:
            begin
              x := 1;
              y := 2;
              z := 3
            end
        
        Returns:
            TreeNode: Nó representando bloco composto
        """
        node = TreeNode("M")  # M = Bloco composto
        
        # begin
        begin_token = self.expect(TokenType.BEGIN)
        node.add_child(TreeNode("begin", token=begin_token))
        
        # Lista de comandos
        node.add_child(self.parse_L())
        
        # end
        end_token = self.expect(TokenType.END)
        node.add_child(TreeNode("end", token=end_token))
        
        return node
    
    def parse_N(self):
        """
        N -> if B then C | if B then C else C
        
        Parseia estrutura condicional (if-then-else).
        O 'else' é opcional.
        
        Formato:
            if condição then
              comando
            else
              comando
        
        Returns:
            TreeNode: Nó representando condicional
        """
        node = TreeNode("N")  # N = Condicional
        
        # if
        if_token = self.expect(TokenType.IF)
        node.add_child(TreeNode("if", token=if_token))
        
        # Condição booleana
        node.add_child(self.parse_B())
        
        # then
        then_token = self.expect(TokenType.THEN)
        node.add_child(TreeNode("then", token=then_token))
        
        # Comando do 'then'
        node.add_child(self.parse_C())
        
        # else (opcional)
        if self.peek().type == TokenType.ELSE:
            else_token = self.advance()
            node.add_child(TreeNode("else", token=else_token))
            
            # Comando do 'else'
            node.add_child(self.parse_C())
        
        return node
    
    def parse_P(self):
        """
        P -> while B do C
        
        Parseia estrutura de repetição (while-do).
        
        Formato:
            while condição do
              comando
        
        Returns:
            TreeNode: Nó representando repetição
        """
        node = TreeNode("P")  # P = Repetição
        
        # while
        while_token = self.expect(TokenType.WHILE)
        node.add_child(TreeNode("while", token=while_token))
        
        # Condição booleana
        node.add_child(self.parse_B())
        
        # do
        do_token = self.expect(TokenType.DO)
        node.add_child(TreeNode("do", token=do_token))
        
        # Corpo do laço
        node.add_child(self.parse_C())
        
        return node
    
    def parse_E(self):
        """
        E -> E + E | E - E | E * E | E / E | - E | (E) | id | num
        
        Parseia uma expressão aritmética.
        
        A gramática original tem recursão à esquerda, que foi transformada
        para permitir análise descendente e implementar precedência:
        - Multiplicação e divisão têm maior precedência
        - Adição e subtração têm menor precedência
        - Menos unário tem maior precedência
        
        Returns:
            TreeNode: Nó representando expressão
        """
        return self.parse_E_expr()
    
    def parse_E_expr(self):
        """
        Parseia adição e subtração (menor precedência).
        
        Estratégia: parseia termo e depois repete (operador termo)*
        
        Returns:
            TreeNode: Nó representando expressão de adição/subtração
        """
        node = TreeNode("E")
        
        # Parseia primeiro termo
        left = self.parse_E_term()
        
        # Enquanto houver + ou -
        while self.peek().type in [TokenType.PLUS, TokenType.MINUS]:
            op_token = self.advance()
            right = self.parse_E_term()
            
            # Cria novo nó para operação binária
            op_node = TreeNode("E")
            op_node.add_child(left)
            op_node.add_child(TreeNode(op_token.type.value, token=op_token))
            op_node.add_child(right)
            
            # Resultado vira operando esquerdo para próxima iteração
            left = op_node
        
        node.add_child(left)
        return node
    
    def parse_E_term(self):
        """
        Parseia multiplicação e divisão (maior precedência).
        
        Estratégia: parseia fator e depois repete (operador fator)*
        
        Returns:
            TreeNode: Nó representando termo (multiplicação/divisão)
        """
        # Parseia primeiro fator
        left = self.parse_E_factor()
        
        # Enquanto houver * ou /
        while self.peek().type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op_token = self.advance()
            right = self.parse_E_factor()
            
            # Cria novo nó para operação binária
            op_node = TreeNode("E")
            op_node.add_child(left)
            op_node.add_child(TreeNode(op_token.type.value, token=op_token))
            op_node.add_child(right)
            
            # Resultado vira operando esquerdo para próxima iteração
            left = op_node
        
        return left
    
    def parse_E_factor(self):
        """
        Parseia fator (maior precedência): - F | (E) | id | num
        
        Fatores podem ser:
        - Menos unário: -expressão
        - Expressão entre parênteses: (expressão)
        - Identificador: x, y, total
        - Número: 10, 42, 100
        
        Returns:
            TreeNode: Nó representando fator
        
        Raises:
            SyntaxError: Se não for nenhum dos padrões esperados
        """
        token = self.peek()
        
        if token.type == TokenType.MINUS:
            # Menos unário: - E
            minus_token = self.advance()
            node = TreeNode("E")
            node.add_child(TreeNode("-", token=minus_token))
            node.add_child(self.parse_E_factor())  # Recursão para fator
            return node
        
        elif token.type == TokenType.LEFT_PAREN:
            # Expressão entre parênteses: (E)
            self.advance()  # Consome '('
            node = self.parse_E_expr()  # Parseia expressão completa
            self.expect(TokenType.RIGHT_PAREN)  # Espera ')'
            return node
        
        elif token.type == TokenType.IDENTIFIER:
            # Identificador
            self.advance()
            return TreeNode("id", token=token)
        
        elif token.type == TokenType.NUMBER:
            # Número
            self.advance()
            return TreeNode("num", token=token)
        
        else:
            # Nenhum padrão válido
            raise SyntaxError("Esperado expressão", token)
    
    def parse_B(self):
        """
        B -> E < E | E <= E | E > E | E >= E | E = E | E <> E | id
        
        Parseia expressão booleana (comparação).
        
        Formato: expressão operador_relacional expressão
        Exemplo: x > 10, y = 5, z <> 0
        
        Note: 'id' sozinho também é permitido (para compatibilidade)
        
        Returns:
            TreeNode: Nó representando expressão booleana
        """
        node = TreeNode("B")  # B = Expressão booleana
        
        # Expressão esquerda
        left = self.parse_E()
        
        token = self.peek()
        
        # Se há operador relacional, parseia lado direito
        if token.type in [TokenType.LESS_THAN, TokenType.LESS_EQUAL,
                         TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                         TokenType.EQUAL, TokenType.NOT_EQUAL]:
            
            op_token = self.advance()
            right = self.parse_E()
            
            # Adiciona: esquerda operador direita
            node.add_child(left)
            node.add_child(TreeNode(op_token.type.value, token=op_token))
            node.add_child(right)
        else:
            # Apenas expressão (caso 'id')
            node.add_child(left)
        
        return node


class AnalisadorSintaticoSigmaGUI:
    """
    Interface Gráfica para o Analisador Sintático Sigma-.
    
    Implementa uma interface completa usando Tkinter que permite:
    - Editar código-fonte Sigma-
    - Carregar arquivos de código
    - Executar análise sintática
    - Visualizar árvore sintática hierárquica
    - Selecionar exemplos pré-carregados
    - Ver legenda dos não-terminais
    
    Layout da interface:
    ┌─────────────────────────────────────────────────┐
    │ Título                                          │
    ├──────────┬──────────────────────────────────────┤
    │ Controles│ Código Fonte                         │
    │ Exemplos │                                      │
    │ Legenda  ├──────────────────────────────────────┤
    │          │ Árvore Sintática                     │
    │          │                                      │
    ├──────────┴──────────────────────────────────────┤
    │ Barra de Status                                 │
    └─────────────────────────────────────────────────┘
    
    Cores e Tema:
    - Background: #f0f0f0 (cinza claro)
    - Botões: #0078d4 (azul moderno)
    - Texto: #333333 (cinza escuro)
    - Sucesso: #00aa00 (verde)
    - Erro: #cc0000 (vermelho)
    """
    
    def __init__(self):
        """
        Inicializa a aplicação GUI.
        
        Cria a janela principal, configura tema visual e inicializa
        variáveis de estado da aplicação.
        """
        # =====================================================================
        # Configuração da janela principal
        # =====================================================================
        self.root = tk.Tk()
        self.root.title("Analisador Sintático - Sigma- (14 Não-Terminais)")
        self.root.geometry("1400x900")  # Tamanho inicial
        self.root.configure(bg='#f0f0f0')  # Cor de fundo

        # =====================================================================
        # Variáveis de estado da aplicação
        # =====================================================================
        self.current_file = None     # Caminho do arquivo carregado
        self.examples = []           # Lista de exemplos pré-carregados
        self.syntax_tree = None      # Árvore sintática gerada

        # =====================================================================
        # Inicialização da interface
        # =====================================================================
        self.setup_modern_theme()    # Configura estilo visual (cores, fontes)
        self.setup_ui()              # Cria componentes da interface
        self.load_examples()         # Carrega exemplos pré-definidos

    def setup_modern_theme(self):
        """
        Configura o tema visual moderno da aplicação.
        
        Define estilos para todos os componentes Tkinter usando ttk.Style.
        Cores seguem paleta moderna e profissional.
        """
        style = ttk.Style()
        style.theme_use('clam')  # Tema base mais moderno

        # Frames e containers
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelFrame', background='#f0f0f0', foreground='#333333')
        style.configure('TLabelFrame.Label', background='#f0f0f0', foreground='#333333')
        
        # Labels
        style.configure('TLabel', background='#f0f0f0', foreground='#333333')
        
        # Botões - Azul moderno
        style.configure('TButton', background='#0078d4', foreground='#ffffff')
        style.map('TButton', background=[('active', '#106ebe')])

        # TreeView (não usado, mas configurado)
        style.configure('Treeview', background='#ffffff', foreground='#333333',
                        fieldbackground='#ffffff', borderwidth=1)
        style.configure('Treeview.Heading', background='#e1e1e1', foreground='#333333')

        # Scrollbars
        style.configure('Vertical.TScrollbar', background='#e1e1e1', troughcolor='#f0f0f0')

    def setup_ui(self):
        """
        Cria e posiciona todos os componentes da interface.
        
        Estrutura hierárquica:
        - main_frame (container principal)
          - title_frame (cabeçalho)
          - controls_frame (painel esquerdo)
            - Botões de ação
            - Legenda de não-terminais
            - Lista de exemplos
          - content_frame (painel direito)
            - source_frame (editor de código)
            - results_frame (visualizador de árvore)
          - status_frame (barra de status)
        """
        # =====================================================================
        # Frame principal com padding
        # =====================================================================
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar redimensionamento responsivo
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)  # Coluna do conteúdo expande
        main_frame.rowconfigure(1, weight=1)     # Linha principal expande

        # =====================================================================
        # CABEÇALHO - Título e subtítulo
        # =====================================================================
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="Analisador Sintático - Sigma-",
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(
            title_frame,
            text="Gramática com 14 Não-Terminais: S, D, V, T, I, L, C, A, R, W, F, G, M, N, P, E, B",
            font=('Segoe UI', 10)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # =====================================================================
        # PAINEL ESQUERDO - Controles, legenda e exemplos
        # =====================================================================
        controls_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controls_frame.grid(
            row=1, column=0,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            padx=(0, 10)
        )

        # ─────────────────────────────────────────────────────────────────────
        # Botões de ação
        # ─────────────────────────────────────────────────────────────────────
        ttk.Button(
            controls_frame,
            text="Carregar Arquivo",
            command=self.load_file
        ).pack(fill=tk.X, pady=3)

        ttk.Button(
            controls_frame,
            text="Analisar Sintaxe",
            command=self.analyze_syntax
        ).pack(fill=tk.X, pady=3)

        ttk.Button(
            controls_frame,
            text="Limpar Tudo",
            command=self.clear_all
        ).pack(fill=tk.X, pady=3)

        # Separador visual
        separator = ttk.Separator(controls_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)

        # ─────────────────────────────────────────────────────────────────────
        # Legenda dos não-terminais
        # ─────────────────────────────────────────────────────────────────────
        info_label = ttk.Label(
            controls_frame,
            text="Não-Terminais:",
            font=('Segoe UI', 10, 'bold')
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))

        # Texto da legenda (não editável)
        info_text = tk.Text(
            controls_frame,
            height=10,
            width=25,
            font=('Courier New', 8),
            bg='#f9f9f9',
            fg='#2c3e50',
            borderwidth=1,
            relief='solid'
        )
        info_text.pack(fill=tk.X, pady=(0, 10))
        
        # Insere legenda formatada
        info_text.insert(1.0, 
            "S = Programa\n"
            "D = Declarações\n"
            "V = Lista variáveis\n"
            "T = Tipo\n"
            "I = Lista ids\n"
            "L = Lista comandos\n"
            "C = Comando\n"
            "A = Atribuição\n"
            "R = Leitura\n"
            "W = Escrita\n"
            "F = Lista stringvar\n"
            "G = StringVar\n"
            "M = Composto\n"
            "N = Condicional\n"
            "P = Repetição\n"
            "E = Expressão\n"
            "B = Expr. Booleana"
        )
        info_text.config(state='disabled')  # Torna somente leitura

        # Outro separador
        separator2 = ttk.Separator(controls_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=15)

        # ─────────────────────────────────────────────────────────────────────
        # Lista de exemplos pré-carregados
        # ─────────────────────────────────────────────────────────────────────
        examples_label = ttk.Label(
            controls_frame,
            text="Exemplos:",
            font=('Segoe UI', 10, 'bold')
        )
        examples_label.pack(anchor=tk.W, pady=(0, 5))

        # Frame para Listbox + Scrollbar
        listbox_frame = ttk.Frame(controls_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Listbox dos exemplos
        self.examples_listbox = tk.Listbox(
            listbox_frame,
            height=8,
            bg='#ffffff',
            fg='#333333',
            selectbackground='#0078d4',
            selectforeground='#ffffff',
            font=('Segoe UI', 9),
            borderwidth=1,
            highlightthickness=1,
            highlightcolor='#0078d4'
        )

        # Scrollbar para a listbox
        examples_scrollbar = ttk.Scrollbar(
            listbox_frame,
            orient=tk.VERTICAL,
            command=self.examples_listbox.yview
        )
        self.examples_listbox.configure(yscrollcommand=examples_scrollbar.set)

        # Posicionamento
        self.examples_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        examples_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Vincula evento de seleção
        self.examples_listbox.bind('<<ListboxSelect>>', self.on_example_select)

        # =====================================================================
        # PAINEL DIREITO - Editor de código e visualizador de árvore
        # =====================================================================
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamento
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)  # Editor expande
        content_frame.rowconfigure(1, weight=1)  # Árvore expande

        # ─────────────────────────────────────────────────────────────────────
        # Editor de código-fonte
        # ─────────────────────────────────────────────────────────────────────
        source_frame = ttk.LabelFrame(
            content_frame,
            text="Código Fonte (Sigma-)",
            padding="10"
        )
        source_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)

        # Área de texto com scroll
        self.source_text = scrolledtext.ScrolledText(
            source_frame,
            height=18,
            font=('Fira Code', 11),  # Fonte monoespaçada para código
            bg='#ffffff',
            fg='#333333',
            insertbackground='#333333',  # Cor do cursor
            selectbackground='#b3d9ff',  # Cor da seleção
            selectforeground='#333333',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor='#0078d4'
        )
        self.source_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ─────────────────────────────────────────────────────────────────────
        # Visualizador da árvore sintática
        # ─────────────────────────────────────────────────────────────────────
        results_frame = ttk.LabelFrame(
            content_frame,
            text="Árvore de Derivação",
            padding="10"
        )
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Área de texto para árvore (somente leitura)
        self.tree_text = scrolledtext.ScrolledText(
            results_frame,
            height=18,
            font=('Courier New', 9),  # Fonte monoespaçada para árvore
            bg='#f9f9f9',
            fg='#2c3e50',
            borderwidth=1,
            highlightthickness=1,
            state='disabled'  # Somente leitura
        )
        self.tree_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # =====================================================================
        # BARRA DE STATUS - Mensagens e indicador visual
        # =====================================================================
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(
            row=2, column=0, columnspan=3,
            sticky=(tk.W, tk.E),
            pady=(10, 0)
        )

        # Variável para mensagem de status
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema pronto para análise sintática")

        # Label de mensagem
        status_bar = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9)
        )
        status_bar.pack(side=tk.LEFT, padx=5)

        # Indicador visual colorido (● verde/amarelo/vermelho)
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            fg='#00aa00',  # Verde inicial
            bg='#f0f0f0',
            font=('Arial', 12)
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=5)

    def load_examples(self):
        """
        Carrega os 5 exemplos pré-definidos de programas Sigma-.
        
        Cada exemplo demonstra diferentes características da linguagem:
        1. Programa mínimo: Declarações e atribuições básicas
        2. Leitura/Escrita: Comandos de I/O
        3. Condicional: Estrutura if-then-else
        4. Repetição: Laço while-do com bloco composto
        5. Completo: Integração de todas as construções
        """
        self.examples = [
            ("1. Programa mínimo",
             "program exemplo;\n"
             "var x, y : integer;\n"
             "begin\n"
             "  x := 10;\n"
             "  y := x + 20\n"
             "end."),
            
            ("2. Leitura/Escrita",
             "program io;\n"
             "var n : integer;\n"
             "begin\n"
             "  readln(n);\n"
             "  writeln(\"Resultado: \", n)\n"
             "end."),
            
            ("3. Condicional",
             "program teste_if;\n"
             "var n : integer;\n"
             "begin\n"
             "  readln(n);\n"
             "  if n > 0 then\n"
             "    writeln(\"positivo\")\n"
             "  else\n"
             "    writeln(\"negativo\")\n"
             "end."),
            
            ("4. Repetição",
             "program teste_while;\n"
             "var i : integer;\n"
             "begin\n"
             "  i := 0;\n"
             "  while i < 10 do\n"
             "  begin\n"
             "    writeln(i);\n"
             "    i := i + 1\n"
             "  end\n"
             "end."),
            
            ("5. Completo",
             "program calc;\n"
             "var a, b, resultado : integer;\n"
             "begin\n"
             "  readln(a, b);\n"
             "  resultado := (a + b) * 2;\n"
             "  if resultado > 100 then\n"
             "    writeln(\"Grande\")\n"
             "  else\n"
             "    writeln(\"Pequeno\")\n"
             "end."),
        ]
        
        # Popula a listbox com os nomes dos exemplos
        self.update_examples_list()

    def update_examples_list(self):
        """
        Atualiza a listbox com os nomes dos exemplos.
        
        Limpa lista atual e insere todos os exemplos carregados.
        """
        self.examples_listbox.delete(0, tk.END)
        for name, _ in self.examples:
            self.examples_listbox.insert(tk.END, name)

    def on_example_select(self, event):
        """
        Callback quando um exemplo é selecionado na listbox.
        
        Carrega o código do exemplo selecionado no editor.
        
        Args:
            event: Evento de seleção do Tkinter
        """
        # Obtém índice do item selecionado
        sel = self.examples_listbox.curselection()
        if not sel:
            return
        
        index = sel[0]
        _, code = self.examples[index]
        
        # Limpa editor e insere código do exemplo
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, code)
        
        # Atualiza status
        self.status_var.set(f"Exemplo carregado")
        self.status_indicator.config(fg='#00aa00')  # Verde

    def load_file(self):
        """
        Abre diálogo para carregar arquivo de código.
        
        Permite selecionar arquivo .txt ou qualquer outro e
        carrega seu conteúdo no editor.
        """
        # Abre diálogo de seleção de arquivo
        file_path = filedialog.askopenfilename(
            title="Carregar Arquivo de Código (Sigma-)",
            filetypes=[
                ("Arquivos de texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        # Se usuário cancelou, retorna
        if not file_path:
            return
        
        try:
            # Lê arquivo com encoding UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limpa editor e insere conteúdo
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, content)
            
            # Armazena caminho do arquivo
            self.current_file = file_path
            
            # Atualiza status
            self.status_var.set(f"Arquivo carregado: {os.path.basename(file_path)}")
            self.status_indicator.config(fg='#00aa00')  # Verde
            
        except Exception as e:
            # Mostra erro se falhar
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
            self.status_var.set("Erro ao carregar arquivo")
            self.status_indicator.config(fg='#cc0000')  # Vermelho

    def analyze_syntax(self):
        """
        Realiza análise sintática completa do código no editor.
        
        Processo:
        1. Obtém código do editor
        2. Executa análise léxica (Lexer)
        3. Executa análise sintática (Parser)
        4. Gera e exibe árvore sintática
        5. Trata erros e exibe mensagens apropriadas
        """
        # Obtém código do editor (remove espaços no fim)
        source_code = self.source_text.get(1.0, tk.END).strip()
        
        # Verifica se há código para analisar
        if not source_code:
            messagebox.showwarning(
                "Aviso",
                "Por favor, insira algum código para analisar."
            )
            return
        
        try:
            # =================================================================
            # Etapa 1: Atualiza UI para indicar processamento
            # =================================================================
            self.status_var.set("Analisando sintaxe...")
            self.status_indicator.config(fg='#ff8800')  # Amarelo
            self.root.update()  # Força atualização da interface

            # =================================================================
            # Etapa 2: Análise Léxica
            # =================================================================
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            # =================================================================
            # Etapa 3: Análise Sintática
            # =================================================================
            parser = Parser(tokens)
            self.syntax_tree = parser.parse()

            # =================================================================
            # Etapa 4: Exibe Árvore Sintática
            # =================================================================
            self.tree_text.config(state='normal')  # Habilita edição temporária
            self.tree_text.delete(1.0, tk.END)     # Limpa conteúdo
            self.tree_text.insert(1.0, self.syntax_tree.to_string())  # Insere árvore
            self.tree_text.config(state='disabled')  # Volta para somente leitura

            # =================================================================
            # Etapa 5: Indica Sucesso
            # =================================================================
            self.status_var.set(f"Análise sintática concluída com sucesso!")
            self.status_indicator.config(fg='#00aa00')  # Verde

            # Mostra popup de confirmação
            messagebox.showinfo(
                "Sucesso",
                "Análise sintática concluída!\n\n"
                "O programa está sintaticamente correto."
            )

        except LexicalError as e:
            # =================================================================
            # Tratamento de Erro Léxico
            # =================================================================
            self.tree_text.config(state='normal')
            self.tree_text.delete(1.0, tk.END)
            self.tree_text.insert(1.0, f"ERRO LÉXICO:\n\n{str(e)}")
            self.tree_text.config(state='disabled')

            messagebox.showerror("Erro Léxico", str(e))
            self.status_var.set("Erro na análise léxica")
            self.status_indicator.config(fg='#cc0000')  # Vermelho

        except SyntaxError as e:
            # =================================================================
            # Tratamento de Erro Sintático
            # =================================================================
            self.tree_text.config(state='normal')
            self.tree_text.delete(1.0, tk.END)
            self.tree_text.insert(1.0, f"ERRO SINTÁTICO:\n\n{str(e)}")
            self.tree_text.config(state='disabled')

            messagebox.showerror("Erro Sintático", str(e))
            self.status_var.set("Erro na análise sintática")
            self.status_indicator.config(fg='#cc0000')  # Vermelho

        except Exception as e:
            # =================================================================
            # Tratamento de Erro Inesperado
            # =================================================================
            self.tree_text.config(state='normal')
            self.tree_text.delete(1.0, tk.END)
            self.tree_text.insert(1.0, f"ERRO INESPERADO:\n\n{str(e)}")
            self.tree_text.config(state='disabled')

            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            self.status_var.set("Erro inesperado")
            self.status_indicator.config(fg='#cc0000')  # Vermelho

    def clear_all(self):
        """
        Limpa todo o estado da aplicação.
        
        Remove:
        - Código do editor
        - Árvore sintática exibida
        - Seleção de exemplo
        - Referência a arquivo carregado
        
        Restaura estado inicial da aplicação.
        """
        # Limpa editor de código
        self.source_text.delete(1.0, tk.END)

        # Limpa visualizador de árvore
        self.tree_text.config(state='normal')
        self.tree_text.delete(1.0, tk.END)
        self.tree_text.config(state='disabled')

        # Reseta variáveis de estado
        self.syntax_tree = None
        self.current_file = None
        
        # Reseta status
        self.status_var.set("Sistema pronto para análise sintática")
        self.status_indicator.config(fg='#00aa00')  # Verde
        
        # Limpa seleção de exemplo
        self.examples_listbox.selection_clear(0, tk.END)

    def run(self):
        """
        Inicia o loop principal da aplicação Tkinter.
        
        Este método bloqueia até a janela ser fechada.
        """
        self.root.mainloop()


# =============================================================================
# PONTO DE ENTRADA DA APLICAÇÃO
# =============================================================================

def main():
    """
    Função principal que inicializa e executa a aplicação.
    
    Cria instância da GUI e inicia o loop de eventos.
    """
    app = AnalisadorSintaticoSigmaGUI()
    app.run()


# Executa apenas se rodado diretamente (não se importado como módulo)
if __name__ == "__main__":
    main()
