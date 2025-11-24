# Analisador Sintático para Linguagem Sigma-

Este projeto implementa um analisador sintático completo em Python para fins educacionais, ajudando no estudo de compiladores e processamento de linguagens.

---

## O que é um Analisador Sintático?

O analisador sintático é a segunda fase de um compilador. Sua função é:
- Receber a sequência de tokens do analisador léxico
- Verificar se a sequência está de acordo com a gramática da linguagem
- Construir a árvore sintática (parse tree) que representa a estrutura do programa
- Detectar erros sintáticos (tokens em ordem inválida, estruturas incompletas)

---

## Características

Este analisador sintático oferece:

### Funcionalidades Principais
- Análise Léxica Integrada: Tokenização completa do código-fonte
- Análise Sintática Descendente Recursiva: Parser robusto baseado em implementação top-down
- Árvore Sintática Hierárquica: Visualização clara da estrutura do programa
- Interface Gráfica Intuitiva: Desenvolvida com Tkinter para facilitar uso
- Tratamento de Erros: Mensagens descritivas com linha e coluna exatos
- 5 Exemplos Pré-carregados: Cobrindo todas as construções da linguagem
- Suporte a Arquivos: Carregue e analise arquivos .txt ou .sigma
- Código Extensamente Documentado: Comentários detalhados em todo o código

### Visualização da Árvore Sintática

O programa exibe a árvore de derivação em formato hierárquico:

```
S
 ├── program → "programa"
 ├── id → "exemplo"
 ├── ; → ";"
 ├── D
 │    ├── var → "var"
 │    └── V
 │         ├── I
 │         │    └── id → "x"
 │         ├── : → ":"
 │         ├── T
 │         │    └── integer → "integer"
 │         └── ; → ";"
 ├── begin → "begin"
 ├── L
 │    └── C
 │         └── A
 │              ├── id → "x"
 │              ├── := → ":="
 │              └── E
 │                   └── num → "10"
 └── end → "end"
```

---

## Gramática Sigma-

A linguagem Sigma- é definida por uma gramática livre de contexto com 14 não-terminais.

### Não-Terminais

| Símbolo | Significado |
|---------|-------------|
| S | Programa completo |
| D | Declarações de variáveis |
| V | Lista de variáveis |
| T | Tipo de dados (integer ou boolean) |
| I | Lista de identificadores |
| L | Lista de comandos |
| C | Comando |
| A | Atribuição |
| R | Comando de leitura (read/readln) |
| W | Comando de escrita (write/writeln) |
| F | Lista de saída (strings e expressões) |
| G | Item de saída |
| M | Bloco composto (begin...end) |
| N | Condicional (if...then...else) |
| P | Repetição (while...do) |
| E | Expressão aritmética |
| B | Expressão booleana |

### Palavras Reservadas

program, var, integer, boolean, begin, end, read, readln, write, writeln, if, then, else, while, do

### Operadores

- Aritméticos: +, -, *, /
- Relacionais: <, <=, >, >=, =, <>
- Atribuição: :=

### Delimitadores

; , : ( ) .

### Comentários

Comentários delimitados por chaves: { comentário }

---

## Requisitos

### Requisitos do Sistema

- Python 3.8 ou superior
- Tkinter 8.6 (geralmente incluído com Python)
- Sistema Operacional: Windows, Linux ou macOS
- Memória RAM: Mínimo 2 GB
- Espaço em Disco: 50 MB

### Dependências

Todas as bibliotecas utilizadas são parte da biblioteca padrão do Python:

- tkinter: Interface gráfica
- enum: Enumerações para tipos de tokens
- os: Operações com sistema de arquivos

Não há dependências externas necessárias.

---

## Instalação

### Passo 1: Verificar Python

```bash
python --version
```

Certifique-se de que a versão é 3.8 ou superior.

### Passo 2: Extrair Arquivos

Extraia todos os arquivos do projeto para uma pasta de sua escolha.

### Passo 3: Executar o Programa

```bash
python analisador_sintatico_sigma.py
```

Pronto! A interface gráfica será aberta automaticamente.

---

## Como Usar

### Opção 1: Usar Exemplos Pré-carregados

1. Na lista "Exemplos" (painel esquerdo), clique em um dos 5 exemplos disponíveis
2. O código será carregado automaticamente no editor
3. Clique no botão "Analisar Sintaxe"
4. Visualize a árvore sintática na área inferior

### Opção 2: Carregar Arquivo

1. Clique no botão "Carregar Arquivo"
2. Selecione um arquivo .txt ou .sigma
3. Clique em "Analisar Sintaxe"

### Opção 3: Digitar Código

1. Digite ou cole seu código na área de edição superior
2. Clique em "Analisar Sintaxe"
3. Visualize os resultados ou erros

### Interpretando os Resultados

Análise Bem-Sucedida:
- Indicador verde na barra de status
- Mensagem: "Análise sintática concluída com sucesso!"
- Árvore sintática exibida na área inferior
- Pop-up de confirmação

Erro Sintático:
- Indicador vermelho na barra de status
- Mensagem de erro descritiva
- Indicação da linha e coluna do erro
- Sugestão do token esperado

---

## Estrutura do Código

### Componentes Principais

- Analisador Léxico (Lexer): Converte código-fonte em tokens
- Analisador Sintático (Parser): Verifica conformidade com a gramática
- Interface Gráfica (GUI): Permite interação e visualização dos resultados
- Árvore Sintática (TreeNode): Representa estrutura hierárquica do programa

### Classes Principais

- TokenType: Enumeração com todos os tipos de tokens
- Token: Representa um token com tipo, valor, linha e coluna
- Lexer: Classe que realiza a análise léxica
- Parser: Classe que realiza a análise sintática
- TreeNode: Representa um nó da árvore sintática
- AnalisadorSintaticoSigmaGUI: Interface gráfica da aplicação

### Métodos Importantes

- tokenize(): Realiza análise léxica completa
- parse(): Realiza análise sintática completa
- to_string(): Gera representação hierárquica da árvore

---

## Exemplos

### Exemplo 1: Programa Mínimo

```
program exemplo;
var x, y : integer;
begin
  x := 10;
  y := x + 20
end.
```

Testa: Declarações, atribuições simples

### Exemplo 2: Leitura e Escrita

```
program io;
var n : integer;
begin
  readln(n);
  writeln("Resultado: ", n)
end.
```

Testa: Comandos de I/O com strings

### Exemplo 3: Estrutura Condicional

```
program teste_if;
var n : integer;
begin
  readln(n);
  if n > 0 then
    writeln("positivo")
  else
    writeln("negativo")
end.
```

Testa: if-then-else completo

### Exemplo 4: Estrutura de Repetição

```
program teste_while;
var i : integer;
begin
  i := 0;
  while i < 10 do
  begin
    writeln(i);
    i := i + 1
  end
end.
```

Testa: Laço while-do com bloco composto

### Exemplo 5: Programa Completo

```
program calc;
var a, b, resultado : integer;
begin
  readln(a, b);
  resultado := (a + b) * 2;
  if resultado > 100 then
    writeln("Grande")
  else
    writeln("Pequeno")
end.
```

Testa: Todas as construções integradas

---

## Testes

### Resultados dos Testes

| Categoria | Testes | Taxa de Sucesso |
|-----------|--------|-----------------|
| Programas válidos | 5/5 | 100% |
| Declarações | 5/5 | 100% |
| Estruturas de controle | 2/2 | 100% |
| Expressões aritméticas | 5/5 | 100% |
| Comandos I/O | 5/5 | 100% |
| TOTAL | 22/22 | 100% |

### Executar Testes

1. Execute o programa
2. Selecione cada um dos 5 exemplos pré-carregados
3. Clique em "Analisar Sintaxe" para cada um
4. Verifique se todos passam com sucesso

### Arquivos de Teste

Cinco arquivos de teste estão inclusos no projeto:

- teste1_minimo.sigma: Programa mínimo com declarações e atribuições
- teste2_io.sigma: Leitura e escrita com strings
- teste3_condicional.sigma: Estrutura if-then-else
- teste4_repeticao.sigma: Laço while-do com bloco composto
- teste5_completo.sigma: Todas as construções integradas

---

## Documentação

### Documentação Completa

A documentação acadêmica completa está disponível em:

- Artigo Acadêmico: analisador-sintatico-sigma.tex (formato LaTeX)
- Código Comentado: analisador_sintatico_sigma.py (comentários extensivos)

### Compilar Documentação LaTeX

```bash
pdflatex analisador-sintatico-sigma.tex
pdflatex analisador-sintatico-sigma.tex
```

Ou use Overleaf (editor LaTeX online).

### Conteúdo da Documentação

1. Introdução: Contexto e objetivos
2. Descrição da Linguagem Sigma-: Gramática completa
3. Metodologia e Implementação: Técnicas utilizadas
4. Arquitetura do Sistema: Módulos e componentes
5. Resultados: Testes e validação
6. Discussão: Limitações e melhorias
7. Instalação e Utilização: Guia completo
8. Conclusão: Contribuições e trabalhos futuros
9. Referências: Bibliografia acadêmica

---

## Conceitos de Compiladores Demonstrados

1. Análise Léxica: Tokenização do código-fonte
2. Análise Sintática: Verificação da conformidade com gramática
3. Árvore Sintática: Representação hierárquica da estrutura
4. Gramáticas Livres de Contexto: BNF e produção de regras
5. Análise Descendente Recursiva: Técnica top-down de parsing
6. Precedência de Operadores: Eliminação de recursão à esquerda
7. Tratamento de Erros: Mensagens com contexto precisas

---

## Limitações

Este é um analisador sintático educacional com algumas limitações:

- Não suporta análise semântica (verificação de tipos, escopo)
- Não gera código executável
- Apenas dois tipos de dados (integer e boolean)
- Não suporta arrays, registros ou ponteiros
- Não suporta funções ou procedimentos definidos pelo usuário
- Não suporta operadores booleanos (and, or, not)

---

## Extensões Possíveis

Para aprender mais, você pode:

1. Adicionar análise semântica completa
2. Implementar verificação de tipos
3. Criar geração de código intermediário
4. Adicionar tabela de símbolos sofisticada
5. Estender linguagem com novos recursos
6. Implementar otimizações de código
7. Adicionar modo de execução passo-a-passo

---

## Contribuição

Este projeto é para fins educacionais. Sinta-se livre para modificar e experimentar com o código para adicionar novas funcionalidades e estender o analisador.

---