#!/usr/bin/env python3
"""
Check type hints in the project and report statistics.
"""

import ast
import os
import sys
from typing import Dict


def analyze_file(filepath: str) -> Dict[str, any]:
    """Analyze type hints in a Python file."""
    with open(filepath, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "filepath": filepath,
            "total_functions": 0,
            "functions_with_hints": 0,
            "percentage": 0,
            "needs_improvement": False,
        }

    total_functions = 0
    functions_with_hints = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip private methods starting with __ (except __init__)
            if node.name.startswith("__") and node.name != "__init__":
                continue

            total_functions += 1

            # Check if function has return type hint
            has_return_hint = node.returns is not None

            # Check if args have type hints
            args_with_hints = 0
            args_total = 0

            for arg in node.args.args:
                args_total += 1
                if arg.annotation is not None:
                    args_with_hints += 1

            # Check if all args have hints (excluding self)
            all_args_hinted = True
            for i, arg in enumerate(node.args.args):
                if arg.arg == "self" and i == 0:
                    continue  # self doesn't need type hint
                if arg.annotation is None:
                    all_args_hinted = False
                    break

            if has_return_hint and all_args_hinted:
                functions_with_hints += 1

    percentage = (functions_with_hints / total_functions * 100) if total_functions > 0 else 0

    return {
        "filepath": filepath,
        "total_functions": total_functions,
        "functions_with_hints": functions_with_hints,
        "percentage": percentage,
        "needs_improvement": percentage < 80 and total_functions > 0,
    }


def main():
    """Main function to check typing in the project."""
    print("🔍 Checking type hints in LunVex Code project...")
    print("=" * 80)

    # Analyze all Python files in the main package
    results = []

    for root, dirs, files in os.walk("lunvex_code"):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                result = analyze_file(filepath)
                results.append(result)

    # Sort by percentage (lowest first)
    results.sort(key=lambda x: x["percentage"])

    # Print summary
    total_files = len(results)
    files_needing_improvement = sum(1 for r in results if r["needs_improvement"])
    avg_percentage = sum(r["percentage"] for r in results) / total_files if total_files > 0 else 0

    print("\n📊 Summary:")
    print(f"   Total files analyzed: {total_files}")
    print(f"   Files needing improvement: {files_needing_improvement}")
    print(f"   Average type hint coverage: {avg_percentage:.1f}%")

    # Print files needing improvement
    if files_needing_improvement > 0:
        print("\n⚠️  Files needing type hint improvements (below 80%):")
        print("-" * 80)

        for result in results:
            if result["needs_improvement"]:
                status = "🔴" if result["percentage"] < 50 else "🟡"
                print(
                    f"{status} {result['filepath']:40} {result['functions_with_hints']:3}/{result['total_functions']:3} ({result['percentage']:5.1f}%)"
                )

    # Print best files
    print("\n✅ Files with good type hint coverage:")
    print("-" * 80)

    good_results = [r for r in results if not r["needs_improvement"] and r["total_functions"] > 0]
    for result in good_results[:10]:  # Show top 10
        status = "🟢"
        print(
            f"{status} {result['filepath']:40} {result['functions_with_hints']:3}/{result['total_functions']:3} ({result['percentage']:5.1f}%)"
        )

    if len(good_results) > 10:
        print(f"   ... and {len(good_results) - 10} more files")

    print("\n" + "=" * 80)
    print("💡 Recommendations:")
    print("1. Focus on files with 🔴 status first")
    print("2. Use the script: scripts/improve_typing.py for suggestions")
    print("3. Run: python -m mypy lunvex_code/ --ignore-missing-imports")
    print("4. Add type hints to public APIs first")

    # Return exit code based on whether improvements are needed
    if files_needing_improvement > 0:
        print(f"\n❌ {files_needing_improvement} files need type hint improvements")
        sys.exit(1)
    else:
        print("\n✅ All files have good type hint coverage!")
        sys.exit(0)


if __name__ == "__main__":
    main()
