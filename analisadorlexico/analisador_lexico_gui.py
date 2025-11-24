#!/usr/bin/env python3
"""
Analisador Léxico com Interface Gráfica
Versão melhorada com GUI usando tkinter e leitura de arquivos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from enum import Enum
import os
import re


class TokenType(Enum):
    """Enumeração dos tipos de tokens reconhecidos pelo analisador léxico"""
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
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Operadores aritméticos
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    
    # Operadores de comparação
    ASSIGN = "ASSIGN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    GREATER_EQUAL = "GREATER_EQUAL"
    
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
    COMMENT = "COMMENT"


class Token:
    """Representa um token encontrado durante a análise léxica"""
    
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.value}, {repr(self.value)}, {self.line}:{self.column})"


class LexicalError(Exception):
    """Exceção para erros léxicos"""
    
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro léxico na linha {line}, coluna {column}: {message}")


class Lexer:
    """Analisador léxico que converte código fonte em tokens"""
    
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.current = 0
        self.line = 1
        self.column = 1
        
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
    
    def is_at_end(self):
        """Verifica se chegou ao final do código fonte"""
        return self.current >= len(self.source)
    
    def advance(self):
        """Avança para o próximo caractere"""
        if not self.is_at_end():
            char = self.source[self.current]
            self.current += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return '\0'
    
    def peek(self):
        """Olha o caractere atual sem avançar"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        """Olha o próximo caractere sem avançar"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def add_token(self, token_type, value):
        """Adiciona um token à lista de tokens"""
        token = Token(token_type, value, self.line, self.column - len(str(value)))
        self.tokens.append(token)
    
    def scan_string(self, quote_char):
        """Escaneia uma string literal"""
        value = ""
        
        while self.peek() != quote_char and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 0
            value += self.advance()
        
        if self.is_at_end():
            raise LexicalError(f"String não terminada", self.line, self.column)
        
        # Consome a aspa de fechamento
        self.advance()
        
        return value
    
    def scan_number(self):
        """Escaneia um número (inteiro ou decimal)"""
        value = ""
        
        # Parte inteira
        while self.peek().isdigit():
            value += self.advance()
        
        # Parte decimal
        if self.peek() == '.' and self.peek_next().isdigit():
            value += self.advance()  # Consome o '.'
            
            while self.peek().isdigit():
                value += self.advance()
        
        return value
    
    def scan_identifier(self):
        """Escaneia um identificador ou palavra-chave"""
        value = ""
        
        while (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        
        return value
    
    def skip_comment(self):
        """Pula comentários de linha (//)"""
        while self.peek() != '\n' and not self.is_at_end():
            self.advance()
    
    def tokenize(self):
        """Realiza a análise léxica completa do código fonte"""
        self.tokens = []
        self.current = 0
        self.line = 1
        self.column = 1
        
        while not self.is_at_end():
            char = self.peek()
            
            # Ignora espaços em branco (exceto quebras de linha)
            if char in ' \t\r':
                self.advance()
                continue
            
            # Quebras de linha
            if char == '\n':
                self.add_token(TokenType.NEWLINE, '\\n')
                self.advance()
                continue
            
            # Comentários
            if char == '/' and self.peek_next() == '/':
                comment_start = self.current
                self.skip_comment()
                comment_text = self.source[comment_start:self.current]
                self.add_token(TokenType.COMMENT, comment_text)
                continue
            
            # Strings
            if char in '"\'':
                quote_char = self.advance()
                try:
                    string_value = self.scan_string(quote_char)
                    self.add_token(TokenType.STRING, f"{quote_char}{string_value}{quote_char}")
                except LexicalError as e:
                    raise e
                continue
            
            # Números
            if char.isdigit():
                number_value = self.scan_number()
                self.add_token(TokenType.NUMBER, number_value)
                continue
            
            # Identificadores e palavras-chave
            if char.isalpha() or char == '_':
                identifier = self.scan_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                self.add_token(token_type, identifier)
                continue
            
            # Operadores de dois caracteres
            if self.current + 1 < len(self.source):
                two_char = char + self.peek_next()
                if two_char in self.double_char_tokens:
                    self.advance()  # Primeiro caractere
                    self.advance()  # Segundo caractere
                    self.add_token(self.double_char_tokens[two_char], two_char)
                    continue
            
            # Operadores de um caractere
            if char in self.single_char_tokens:
                self.advance()
                self.add_token(self.single_char_tokens[char], char)
                continue
            
            # Caractere desconhecido
            unknown_char = self.advance()
            raise LexicalError(f"Caractere desconhecido: '{unknown_char}'", 
                             self.line, self.column - 1)
        
        # Adiciona token EOF
        self.add_token(TokenType.EOF, '')
        return self.tokens


class AnalisadorLexicoGUI:
    """Interface gráfica para o analisador léxico"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analisador Léxico - Interface Moderna")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar tema moderno
        self.setup_modern_theme()
        
        # Variáveis
        self.current_file = None
        self.examples = []
        
        self.setup_ui()
        self.load_examples()
    
    def setup_modern_theme(self):
        """Configura tema moderno claro"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores modernas para componentes básicos
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelFrame', background='#f0f0f0', foreground='#333333')
        style.configure('TLabelFrame.Label', background='#f0f0f0', foreground='#333333')
        style.configure('TLabel', background='#f0f0f0', foreground='#333333')
        style.configure('TButton', background='#0078d4', foreground='#ffffff')
        style.map('TButton', background=[('active', '#106ebe')])
        
        # Configurar Treeview moderno
        style.configure('Treeview', background='#ffffff', foreground='#333333', 
                       fieldbackground='#ffffff', borderwidth=1)
        style.configure('Treeview.Heading', background='#e1e1e1', foreground='#333333')
        
        # Configurar Scrollbar
        style.configure('Vertical.TScrollbar', background='#e1e1e1', troughcolor='#f0f0f0')
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título moderno
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="Analisador Léxico", 
                               font=('Segoe UI', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(title_frame, text="Trabalho de Compiladores - Analisador Léxico", 
                                  font=('Segoe UI', 10))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame de controles moderno
        controls_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botões modernos sem ícones
        ttk.Button(controls_frame, text="Carregar Arquivo", 
                  command=self.load_file).pack(fill=tk.X, pady=3)
        
        ttk.Button(controls_frame, text="Carregar Exemplos", 
                  command=self.load_examples_file).pack(fill=tk.X, pady=3)
        
        ttk.Button(controls_frame, text="Analisar Código", 
                  command=self.analyze_code).pack(fill=tk.X, pady=3)
        
        ttk.Button(controls_frame, text="Limpar Tudo", 
                  command=self.clear_all).pack(fill=tk.X, pady=3)
        
        # Separador moderno
        separator = ttk.Separator(controls_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)
        
        # Lista de exemplos moderna
        examples_label = ttk.Label(controls_frame, text="Exemplos Disponíveis:", 
                                  font=('Segoe UI', 10, 'bold'))
        examples_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para listbox com scrollbar
        listbox_frame = ttk.Frame(controls_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.examples_listbox = tk.Listbox(listbox_frame, height=10, 
                                          bg='#ffffff', fg='#333333', 
                                          selectbackground='#0078d4',
                                          selectforeground='#ffffff',
                                          font=('Segoe UI', 9),
                                          borderwidth=1, highlightthickness=1,
                                          highlightcolor='#0078d4')
        
        examples_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                          command=self.examples_listbox.yview)
        self.examples_listbox.configure(yscrollcommand=examples_scrollbar.set)
        
        self.examples_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        examples_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.examples_listbox.bind('<<ListboxSelect>>', self.on_example_select)
        
        # Frame principal de conteúdo
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Área de código fonte moderna
        source_frame = ttk.LabelFrame(content_frame, text="Código Fonte", padding="10")
        source_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)
        
        self.source_text = scrolledtext.ScrolledText(source_frame, height=18, 
                                                    font=('Fira Code', 11),
                                                    bg='#ffffff', fg='#333333',
                                                    insertbackground='#333333',
                                                    selectbackground='#b3d9ff',
                                                    selectforeground='#333333',
                                                    borderwidth=1, highlightthickness=1,
                                                    highlightcolor='#0078d4')
        self.source_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Área de resultados moderna
        results_frame = ttk.LabelFrame(content_frame, text="Tokens Encontrados", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview moderna para tokens
        columns = ('Valor', 'Tipo')
        self.tokens_tree = ttk.Treeview(results_frame, columns=columns, show='headings', 
                                       height=18)
        
        # Configurar colunas sem ícones
        self.tokens_tree.heading('Valor', text='Valor')
        self.tokens_tree.heading('Tipo', text='Tipo')
        
        self.tokens_tree.column('Valor', width=300, anchor='w')
        self.tokens_tree.column('Tipo', width=250, anchor='center')
        
        # Scrollbar moderna para treeview
        tokens_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                        command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tokens_scrollbar.set)
        
        self.tokens_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tokens_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar moderna
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Sistema pronto para análise")
        
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              font=('Segoe UI', 9))
        status_bar.pack(side=tk.LEFT, padx=5)
        
        # Indicador de status visual
        self.status_indicator = tk.Label(status_frame, text="●", 
                                        fg='#00aa00', bg='#f0f0f0', 
                                        font=('Arial', 12))
        self.status_indicator.pack(side=tk.RIGHT, padx=5)
    
    def load_examples(self):
        """Carrega exemplos padrão"""
        default_examples = [
            ("Expressão aritmética", "x = 10 + 20 * 3.5"),
            ("Estrutura condicional", 'if (idade >= 18) {\n    status = "adulto"\n} else {\n    status = "menor"\n}'),
            ("Função com loop", 'function calcular(n) {\n    var resultado = 0\n    for i = 1; i <= n; i = i + 1 {\n        resultado = resultado + i\n    }\n    return resultado\n}'),
            ("Operadores lógicos", 'if (x > 0 and y != 0) or not z {\n    // Este é um comentário\n    print("Condição verdadeira")\n}')
        ]
        
        self.examples = default_examples
        self.update_examples_list()
    
    def load_examples_file(self):
        """Carrega exemplos de um arquivo"""
        file_path = filedialog.askopenfilename(
            title="Carregar Arquivo de Exemplos",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Parse do arquivo de exemplos
                examples = []
                sections = content.split('---')
                
                for section in sections:
                    lines = section.strip().split('\n')
                    if len(lines) >= 2:
                        name = lines[0].strip()
                        code = '\n'.join(lines[1:]).strip()
                        if name and code:
                            examples.append((name, code))
                
                if examples:
                    self.examples = examples
                    self.update_examples_list()
                    self.status_var.set(f"Carregados {len(examples)} exemplos de {os.path.basename(file_path)}")
                    self.status_indicator.config(fg='#00aa00')  # Verde para sucesso
                else:
                    messagebox.showwarning("Aviso", "Nenhum exemplo válido encontrado no arquivo.")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                self.status_var.set("Erro ao carregar exemplos")
                self.status_indicator.config(fg='#cc0000')  # Vermelho para erro
    
    def update_examples_list(self):
        """Atualiza a lista de exemplos na interface"""
        self.examples_listbox.delete(0, tk.END)
        for name, _ in self.examples:
            self.examples_listbox.insert(tk.END, name)
    
    def on_example_select(self, event):
        """Manipula a seleção de um exemplo"""
        selection = self.examples_listbox.curselection()
        if selection:
            index = selection[0]
            _, code = self.examples[index]
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, code)
            self.status_var.set(f"Exemplo {index + 1} carregado")
            self.status_indicator.config(fg='#00aa00')  # Verde para sucesso
    
    def load_file(self):
        """Carrega um arquivo de código"""
        file_path = filedialog.askopenfilename(
            title="Carregar Arquivo de Código",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, content)
                self.current_file = file_path
                self.status_var.set(f"Arquivo carregado: {os.path.basename(file_path)}")
                self.status_indicator.config(fg='#00aa00')  # Verde para sucesso
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                self.status_var.set("Erro ao carregar arquivo")
                self.status_indicator.config(fg='#cc0000')  # Vermelho para erro
    
    def analyze_code(self):
        """Analisa o código fonte e exibe os tokens"""
        source_code = self.source_text.get(1.0, tk.END).strip()
        
        if not source_code:
            messagebox.showwarning("Aviso", "Por favor, insira algum código para analisar.")
            return
        
        try:
            # Atualizar status para análise em progresso
            self.status_var.set("Analisando código...")
            self.status_indicator.config(fg='#ff8800')  # Laranja para processando
            self.root.update()
            
            # Limpar resultados anteriores
            for item in self.tokens_tree.get_children():
                self.tokens_tree.delete(item)
            
            # Analisar código
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            # Exibir tokens
            for token in tokens:
                value_display = repr(token.value) if token.type == TokenType.STRING else token.value
                self.tokens_tree.insert('', tk.END, values=(
                    value_display,
                    token.type.value
                ))
            
            self.status_var.set(f"Análise concluída! {len(tokens)} tokens encontrados")
            self.status_indicator.config(fg='#00aa00')  # Verde para sucesso
            
        except LexicalError as e:
            messagebox.showerror("Erro Léxico", str(e))
            self.status_var.set("Erro na análise léxica")
            self.status_indicator.config(fg='#cc0000')  # Vermelho para erro
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            self.status_var.set("Erro inesperado na análise")
            self.status_indicator.config(fg='#cc0000')  # Vermelho para erro
    
    def clear_all(self):
        """Limpa todas as áreas de texto"""
        self.source_text.delete(1.0, tk.END)
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        self.current_file = None
        self.status_var.set("Campos limpos - Sistema pronto")
        self.status_indicator.config(fg='#00aa00')  # Verde para pronto
        self.examples_listbox.selection_clear(0, tk.END)
    
    def run(self):
        """Inicia a interface gráfica"""
        self.root.mainloop()


def main():
    """Função principal"""
    app = AnalisadorLexicoGUI()
    app.run()


if __name__ == "__main__":
    main()