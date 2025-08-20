# Analisador Léxico Simples em Python

Este projeto implementa um analisador léxico (lexer) simples em Python para fins educacionais, ajudando no estudo de compiladores e processamento de linguagens.

## O que é um Analisador Léxico?

O analisador léxico é a primeira fase de um compilador. Sua função é:
- Ler o código fonte caractere por caractere
- Agrupar caracteres em unidades significativas chamadas **tokens**
- Classificar cada token por tipo (número, identificador, operador, etc.)
- Detectar erros léxicos (caracteres inválidos)

## Funcionalidades

Este analisador léxico reconhece:

### Tipos de Tokens
- **Números**: inteiros e decimais (ex: `42`, `3.14`)
- **Identificadores**: nomes de variáveis e funções (ex: `variavel`, `minha_funcao`)
- **Strings**: texto entre aspas (ex: `"hello"`, `'world'`)
- **Palavras-chave**: `if`, `else`, `while`, `for`, `function`, `return`, `var`, `and`, `or`, `not`
- **Operadores aritméticos**: `+`, `-`, `*`, `/`, `%`
- **Operadores de comparação**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Operadores lógicos**: `and`, `or`, `not`
- **Atribuição**: `=`
- **Delimitadores**: `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`
- **Comentários**: linhas que começam com `//`

### Tratamento de Erros
- Detecta caracteres inválidos
- Reporta linha e coluna do erro
- Detecta strings não fechadas

## Como Usar

### Executar o programa
```bash
python analisador_lexico.py
```

O programa oferece:
1. **Exemplos pré-definidos**: demonstra a análise de diferentes tipos de código
2. **Modo interativo**: permite inserir seu próprio código para análise

### Usar como biblioteca
```python
from analisador_lexico import Lexer, LexicalError

# Criar o analisador
codigo = "x = 10 + 20 * 3.5"
lexer = Lexer(codigo)

try:
    # Realizar a análise léxica
    tokens = lexer.tokenize()
    
    # Imprimir os tokens
    lexer.print_tokens()
    
    # Ou acessar os tokens individualmente
    for token in tokens:
        print(f"Tipo: {token.type}, Valor: {token.value}, Linha: {token.line}, Coluna: {token.column}")
        
except LexicalError as e:
    print(f"Erro léxico: {e}")
```

## Estrutura do Código

### Classes Principais

- **`TokenType`**: Enumeração com todos os tipos de tokens
- **`Token`**: Representa um token com tipo, valor, linha e coluna
- **`Lexer`**: Classe principal que realiza a análise léxica
- **`LexicalError`**: Exceção para erros léxicos

### Métodos Importantes

- **`tokenize()`**: Realiza a análise completa e retorna lista de tokens
- **`print_tokens()`**: Imprime tokens de forma formatada
- **`current_char()`**: Retorna o caractere atual
- **`advance()`**: Avança para o próximo caractere
- **`read_number()`**: Lê números inteiros e decimais
- **`read_identifier()`**: Lê identificadores e palavras-chave
- **`read_string()`**: Lê strings com suporte a caracteres de escape

## Exemplos de Uso

### Exemplo 1: Expressão Aritmética
```
Código: x = 10 + 20 * 3.5

Tokens:
IDENTIFIER     x               1      1
ASSIGN         =               1      3
NUMBER         10              1      5
PLUS           +               1      8
NUMBER         20              1      10
MULTIPLY       *               1      13
NUMBER         3.5             1      15
EOF                            1      18
```

### Exemplo 2: Estrutura Condicional
```
Código: if (idade >= 18) { status = "adulto" }

Tokens:
IF             if              1      1
LEFT_PAREN     (               1      4
IDENTIFIER     idade           1      5
GREATER_EQUAL  >=              1      11
NUMBER         18              1      14
RIGHT_PAREN    )               1      16
LEFT_BRACE     {               1      18
IDENTIFIER     status          1      20
ASSIGN         =               1      27
STRING         'adulto'        1      29
RIGHT_BRACE    }               1      38
EOF                            1      39
```

## Conceitos de Compiladores Demonstrados

1. **Tokenização**: Processo de quebrar o código em unidades léxicas
2. **Reconhecimento de padrões**: Uso de autômatos finitos para reconhecer tokens
3. **Tratamento de erros**: Detecção e reporte de erros léxicos
4. **Tabela de símbolos**: Mapeamento de palavras-chave
5. **Posicionamento**: Rastreamento de linha e coluna para debug

## Limitações

Este é um analisador léxico educacional e possui algumas limitações:
- Não suporta números em notação científica
- Não suporta caracteres Unicode especiais
- Comentários apenas de linha (`//`), não de bloco (`/* */`)
- Não suporta strings multi-linha

## Extensões Possíveis

Para aprender mais, você pode:
1. Adicionar suporte para mais tipos de tokens
2. Implementar comentários de bloco
3. Adicionar suporte para números hexadecimais
4. Criar um analisador sintático (parser) que use estes tokens
5. Implementar uma tabela de símbolos mais sofisticada

## Contribuição

Este projeto é para fins educacionais. Sinta-se livre para modificar e experimentar!