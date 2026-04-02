from __future__ import annotations

import os
import sys

from token_types import TOKEN_TYPES
from lexer import Lexer


_EXAMPLES: list[tuple[str, str]] = [
    (
        "Exemplo 1 — Hello World com #include",
        """\
#include <stdio.h>
int main(void) {
    printf("Hello, world!\\n");
    return 0;
}""",
    ),
    (
        "Exemplo 2 — Tipos básicos e operações",
        """\
int main(void) {
    int x = 42;
    float y = 3.14;
    char c = 'a';
    x = x + 10;
    y = y * 2;
    c = '\\n';
    return x;
}""",
    ),
    (
        "Exemplo 3 — Estruturas de controle",
        """\
int main(void) {
    int i = 0;
    while (i < 5) {
        if (i % 2 == 0) {
            printf("even\\n");
        } else {
            printf("odd\\n");
        }
        i++;
    }
    return 0;
}""",
    ),
    (
        "Exemplo 4 — Erros léxicos (demonstração)",
        """\
int main(void) {
    float pi = 3,14;
    float e  = 2, 718;
    char *s  = "nao fechada;
    int 3var = 10;
    int ok   = 42abc;
    return 0;
}""",
    ),
]


def format_output(lexer: Lexer, title: str = "Análise Léxica") -> None:
    W   = 72
    SEP = "═" * W

    print(f"\n╔{SEP}╗")
    print(f"║  {title:<{W - 2}}║")
    print(f"╚{SEP}╝")

    visible = [t for t in lexer.tokens if t.tipo != TOKEN_TYPES["EOF"]]
    print(f"\n  📋  LISTA DE TOKENS  ({len(visible)} token(s))\n")
    print(f"  {'#':<5} {'TIPO':<18} {'LEXEMA':<30} ATRIBUTO")
    print(f"  {'─' * W}")

    for i, tok in enumerate(visible, 1):
        attr = str(tok.atributo) if tok.atributo is not None else "—"
        lex  = repr(tok.lexema) if ("\n" in tok.lexema or "\t" in tok.lexema) else tok.lexema
        attr_display = attr if len(attr) <= 40 else attr[:37] + "..."
        print(f"  {i:<5} {tok.tipo:<18} {lex:<30} {attr_display}")

    sym = lexer.symbol_table
    print(f"\n  📚  TABELA DE SÍMBOLOS  ({len(sym)} identificador(es) único(s))\n")
    if sym:
        print(f"  {'IDENTIFICADOR':<32} {'OCORRÊNCIAS':>12}")
        print(f"  {'─' * 46}")
        for name, cnt in sorted(sym.items()):
            print(f"  {name:<32} {cnt:>12}")
    else:
        print("  (nenhum identificador encontrado)")

    print(f"\nERROS LÉXICOS  ({len(lexer.errors)} erro(s))\n")
    if lexer.errors:
        for err in lexer.errors:
            print(f"  → {err}")
    else:
        print("Nenhum erro léxico encontrado.")

    print(f"\n  Total de tokens produzidos : {len(visible)}")
    print(f"  Identificadores únicos     : {len(sym)}")
    print(f"  Erros léxicos              : {len(lexer.errors)}")
    print(f"\n{'═' * (W + 2)}\n")


_HEADER = r"""
  ██╗     ███████╗██╗  ██╗███████╗██████╗
  ██║     ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗
  ██║     █████╗   ╚███╔╝ █████╗  ██████╔╝
  ██║     ██╔══╝   ██╔██╗ ██╔══╝  ██╔══██╗
  ███████╗███████╗██╔╝ ██╗███████╗██║  ██║
  ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""

_SUBTITLE = """\
  ┌─────────────────────────────────────────────────────────────────────┐
  │                          Analisador Léxico                          │
  └─────────────────────────────────────────────────────────────────────┘
"""

_MENU = """\
  ┌─────────────────────────────────┐
  │           MENU PRINCIPAL        │
  ├─────────────────────────────────┤
  │  1 · Abrir arquivo (.c / .txt)  │
  │  2 · Digitar código no terminal │
  │  3 · Executar exemplos prontos  │
  │  4 · Sair                       │
  └─────────────────────────────────┘
"""


def _print_header() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")
    print(_HEADER)
    print(_SUBTITLE)


def _print_menu() -> None:
    print(_MENU)


def _handle_file() -> None:
    filepath: str | None = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de código-fonte",
            filetypes=[
                ("Arquivos C",   "*.c"),
                ("Arquivos C++", "*.cpp *.cc *.cxx"),
                ("Texto",        "*.txt"),
                ("Todos",        "*.*"),
            ],
        )
        root.destroy()
    except Exception:
        print("\n  [!] Interface gráfica indisponível.")
        print("  Digite o caminho do arquivo: ", end="", flush=True)
        filepath = input().strip()

    if not filepath:
        print("\n  [!] Nenhum arquivo selecionado.\n")
        _pause()
        return

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            source = fh.read()
    except FileNotFoundError:
        print(f"\n  [!] Arquivo não encontrado: {filepath!r}\n")
        _pause()
        return
    except OSError as exc:
        print(f"\n  [!] Erro ao ler o arquivo: {exc}\n")
        _pause()
        return

    if not source.strip():
        print("\n  [!] Arquivo vazio. Nada a analisar.\n")
        _pause()
        return

    print(f"\n  Arquivo  : {filepath}")
    print(f"  Tamanho  : {len(source)} caracteres\n")
    lexer = Lexer(source)
    lexer.tokenize()
    format_output(lexer, f"Análise: {os.path.basename(filepath)}")
    _pause()


def _handle_interactive() -> None:
    print("\n  Cole ou digite o código C-like abaixo.")
    print("  Encerre com EOF  (Ctrl+D no Linux/macOS · Ctrl+Z+Enter no Windows)\n")
    print("  " + "─" * 60)
    lines: list[str] = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass
    source = "\n".join(lines)
    print("  " + "─" * 60)
    if not source.strip():
        print("\n  [!] Entrada vazia. Nada a analisar.\n")
        _pause()
        return
    lexer = Lexer(source)
    lexer.tokenize()
    format_output(lexer, "Análise: entrada interativa")
    _pause()


def _handle_examples() -> None:
    print(f"\n  Executando {len(_EXAMPLES)} exemplo(s) hardcoded...\n")
    for title, source in _EXAMPLES:
        lexer = Lexer(source)
        lexer.tokenize()
        format_output(lexer, title)
    _pause()


def _pause() -> None:
    print("  Pressione Enter para voltar ao menu...", end="", flush=True)
    try:
        input()
    except EOFError:
        pass


def main() -> None:
    _print_header()
    while True:
        _print_menu()
        print("  Escolha uma opção: ", end="", flush=True)
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Até logo!\n")
            sys.exit(0)
        if choice == "1":
            _print_header()
            _handle_file()
            _print_header()
        elif choice == "2":
            _print_header()
            _handle_interactive()
            _print_header()
        elif choice == "3":
            _print_header()
            _handle_examples()
            _print_header()
        elif choice == "4":
            print("\n  Até logo!\n")
            sys.exit(0)
        else:
            print(f"\n  [!] Opção inválida: {choice!r}. Digite 1, 2, 3 ou 4.\n")


if __name__ == "__main__":
    main()