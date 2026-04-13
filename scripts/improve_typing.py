#!/usr/bin/env python3
"""
Script to improve type hints in LunVex Code project.
This script adds missing type hints to function signatures.
"""

import ast
import os
from typing import List, Optional, Tuple


def parse_function_signature(node: ast.FunctionDef) -> Tuple[str, List[str], Optional[str]]:
    """Parse a function signature and return its components."""
    # Get function name
    func_name = node.name

    # Get arguments
    args = []
    for arg in node.args.args:
        if arg.arg != "self":
            args.append(arg.arg)

    # Get return type
    return_type = ast.unparse(node.returns) if node.returns else None

    return func_name, args, return_type


def needs_type_hints(node: ast.FunctionDef) -> bool:
    """Check if a function needs type hints."""
    # Skip private methods starting with __ (except __init__)
    if node.name.startswith("__") and node.name != "__init__":
        return False

    # Check if all arguments have type hints
    for arg in node.args.args:
        if arg.annotation is None:
            return True

    # Check if return type is specified
    if node.returns is None:
        return True

    return False


def generate_type_hint_suggestion(node: ast.FunctionDef) -> str:
    """Generate a type hint suggestion for a function."""
    lines = []

    # Function signature
    args_with_types = []
    for arg in node.args.args:
        arg_name = arg.arg
        if arg.annotation:
            arg_type = ast.unparse(arg.annotation)
        else:
            # Default type suggestions based on argument name
            arg_type = suggest_type_from_name(arg_name)
        args_with_types.append(f"{arg_name}: {arg_type}")

    signature = f"def {node.name}({', '.join(args_with_types)})"

    if node.returns:
        return_type = ast.unparse(node.returns)
    else:
        return_type = suggest_return_type(node)

    signature += f" -> {return_type}:"
    lines.append(signature)

    # Docstring template
    lines.append('    """')
    lines.append(f"    {node.name.replace('_', ' ').title()}.")
    lines.append("")

    # Add parameter descriptions
    for arg in node.args.args:
        if arg.arg != "self":
            lines.append("    Args:")
            lines.append(f"        {arg.arg}: Description")
            break

    if node.returns:
        lines.append("")
        lines.append("    Returns:")
        lines.append("        Description")

    lines.append('    """')

    return "\n".join(lines)


def suggest_type_from_name(arg_name: str) -> str:
    """Suggest a type based on argument name."""
    type_mapping = {
        "path": "str",
        "file": "str",
        "content": "str",
        "command": "str",
        "pattern": "str",
        "url": "str",
        "message": "str",
        "task": "str",
        "config": "Dict[str, Any]",
        "data": "Dict[str, Any]",
        "result": "Any",
        "value": "Any",
        "obj": "Any",
        "items": "List[Any]",
        "files": "List[str]",
        "names": "List[str]",
        "count": "int",
        "limit": "int",
        "size": "int",
        "timeout": "int",
        "max_size": "int",
        "verbose": "bool",
        "force": "bool",
        "dry_run": "bool",
    }

    # Check for exact matches first
    if arg_name in type_mapping:
        return type_mapping[arg_name]

    # Check for partial matches
    for key, value in type_mapping.items():
        if key in arg_name:
            return value

    return "Any"


def suggest_return_type(node: ast.FunctionDef) -> str:
    """Suggest a return type based on function name."""
    return_type_mapping = {
        "get_": "Any",
        "find_": "Optional[Any]",
        "create_": "Any",
        "build_": "Any",
        "make_": "Any",
        "generate_": "Any",
        "read_": "str",
        "write_": "bool",
        "save_": "bool",
        "load_": "Any",
        "parse_": "Any",
        "validate_": "bool",
        "check_": "bool",
        "verify_": "bool",
        "execute_": "Any",
        "run_": "Any",
        "process_": "Any",
        "handle_": "Any",
        "init_": "None",
        "setup_": "None",
        "configure_": "None",
        "reset_": "None",
        "clear_": "None",
        "clean_": "None",
        "is_": "bool",
        "has_": "bool",
        "can_": "bool",
        "should_": "bool",
    }

    for prefix, return_type in return_type_mapping.items():
        if node.name.startswith(prefix):
            return return_type

    return "Any"


def analyze_file(filepath: str) -> List[Tuple[str, str]]:
    """Analyze a Python file and find functions needing type hints."""
    with open(filepath, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    suggestions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if needs_type_hints(node):
                suggestion = generate_type_hint_suggestion(node)
                suggestions.append((node.name, suggestion))

    return suggestions


def main():
    """Main function to analyze and suggest type hints."""
    print("Analyzing type hints in LunVex Code project...")
    print("=" * 80)

    # Analyze key files
    key_files = [
        "lunvex_code/agent.py",
        "lunvex_code/async_agent.py",
        "lunvex_code/llm.py",
        "lunvex_code/permissions.py",
        "lunvex_code/tools/base.py",
        "lunvex_code/tools/async_base.py",
    ]

    for filepath in key_files:
        if os.path.exists(filepath):
            print(f"\n📁 {filepath}")
            print("-" * 40)

            suggestions = analyze_file(filepath)

            if suggestions:
                for func_name, suggestion in suggestions:
                    print(f"\nFunction: {func_name}")
                    print("Suggested signature:")
                    print(suggestion)
            else:
                print("✓ All functions have type hints!")

    print("\n" + "=" * 80)
    print("Analysis complete.")
    print("\nTo improve type hints:")
    print("1. Review the suggestions above")
    print("2. Update function signatures in the source files")
    print("3. Run: ruff check --fix lunvex_code/")
    print("4. Run tests to ensure nothing is broken")


if __name__ == "__main__":
    main()
