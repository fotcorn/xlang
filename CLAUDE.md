# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XLang is a Python-based programming language implementation with a compiler and interpreter. The project uses Python 3.12+ and follows a modular architecture with separate components for parsing, validation, and interpretation.

## Commands

### Running XLang Code
```bash
# Run a single XLang file
python main.py examples/fib.xl

# Parse only (outputs AST as JSON)
python main.py --parse-only examples/fib.xl

# Run split input files (for testing with multiple code blocks)
python main.py --split-input-file tests/lit/your_test.xl
```

### Testing
```bash
# Run all lit tests
lit -v tests/lit/

# Run a specific lit test
lit -v tests/lit/basics.xl

# Run unit tests
pytest tests/unit/

# Run unit tests with coverage
pytest --cov=xlang tests/unit/
```

### Code Quality
```bash
# Type checking
mypy xlang/

# Code formatting
black xlang/ tests/

# Linting
flake8 xlang/ tests/
```

### Development Setup
```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

## Architecture

### Core Components

- **`xlang/grammar.lark`**: Lark-based grammar definition for XLang syntax
- **`xlang/parser.py`**: Parser that converts source code to AST using Lark
- **`xlang/transformer.py`**: Transforms Lark parse tree to custom AST nodes
- **`xlang/xl_ast.py`**: AST node definitions using Pydantic models
- **`xlang/validation_pass.py`**: Type checking and semantic validation
- **`xlang/interpreter.py`**: Tree-walking interpreter for executing AST
- **`xlang/xl_builtins.py`**: Built-in functions and methods
- **`xlang/xl_types.py`**: Type system definitions
- **`xlang/interpreter_datatypes.py`**: Runtime data structures

### Execution Flow

1. **Parsing**: `main.py` → `parser.py` → AST via `transformer.py`
2. **Validation**: `validation_pass()` performs type checking and semantic analysis
3. **Interpretation**: `interpreter.py` executes the validated AST

### Testing Framework

The project uses LLVM-style lit testing with FileCheck for integration tests:
- Test files in `tests/lit/` use `.xl` extension
- Tests use `// RUN:` and `// CHECK:` directives
- `%run` substitution expands to `python main.py`
- `%filecheck` substitution expands to the FileCheck binary path

### Type System

XLang supports:
- Primitive types: integers (i8-i64, u8-u64), f32, bool, char, string
- Arrays: `[type]` syntax
- Structs: custom data types with named fields
- Enums: enumeration types

### Error Handling

- `ContextException`: Base for all language errors with source location context
- `InterpreterAssertionError`: Failed assertions (causes interpreter to exit)
- Parse errors are converted to context exceptions with location information