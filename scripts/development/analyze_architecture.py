#!/usr/bin/env python3
"""
Script to analyze project architecture and detect circular imports.
This script is used by the pre-commit hook to prevent circular dependencies.
"""

import ast
import os
import sys
from pathlib import Path


def get_python_files(root_dir: str) -> list[Path]:
    """Get all Python files in the project."""
    python_files = []
    for root, _, files in os.walk(root_dir):
        # Skip hidden directories and __pycache__
        if any(
            part.startswith(".") or part == "__pycache__" for part in Path(root).parts
        ):
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("."):
                python_files.append(Path(root) / file)
    return python_files


def extract_imports(file_path: Path) -> list[str]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports
    except SyntaxError:
        # If we can't parse the file due to syntax error, return empty list
        return []
    except OSError:
        # If we can't read the file, return empty list
        return []


def build_import_graph(python_files: list[Path]) -> dict[str, set[str]]:
    """Build a graph of module imports."""
    graph = {}

    # First, map file paths to module names
    file_to_module = {}
    for file_path in python_files:
        # Convert file path to module name
        parts = file_path.parts
        # Find the src directory
        try:
            src_index = parts.index("src")
            module_parts = parts[src_index:]
            # Remove .py extension
            if module_parts[-1].endswith(".py"):
                module_parts = list(module_parts[:-1]) + [module_parts[-1][:-3]]
            module_name = ".".join(module_parts)
            file_to_module[str(file_path)] = module_name
            graph[module_name] = set()
        except ValueError:
            # Not in src directory, use relative path from current directory
            rel_path = file_path.relative_to(Path("."))
            if str(rel_path).endswith(".py"):
                module_name = str(rel_path)[:-3].replace(os.sep, ".")
            else:
                module_name = str(rel_path).replace(os.sep, ".")
            file_to_module[str(file_path)] = module_name
            graph[module_name] = set()

    # Then extract imports for each file
    for file_path in python_files:
        module_name = file_to_module[str(file_path)]
        imports = extract_imports(file_path)

        # Resolve imports to module names
        for imp in imports:
            # Check if this import corresponds to any of our modules
            for _, mod_name in file_to_module.items():
                # Simple check: if import starts with module name
                if imp == mod_name or imp.startswith(mod_name + "."):
                    graph[module_name].add(mod_name)
                # Also check if module name starts with import (for relative imports)
                elif mod_name == imp or mod_name.startswith(imp + "."):
                    graph[module_name].add(mod_name)

    return graph


def detect_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Detect cycles in the import graph using DFS."""
    visiting = set()
    visited = set()
    path = []
    cycles = []

    def dfs(node: str) -> None:
        if node in visiting:
            # Found a cycle
            try:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
            except ValueError:
                pass
            return

        if node in visited:
            return

        visiting.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            dfs(neighbor)

        path.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


def main() -> int:
    """Main function."""
    # Get project root (current directory)
    project_root = Path(".")

    # Get all Python files
    python_files = get_python_files(str(project_root))

    if not python_files:
        print("No Python files found in project.")
        return 0

    # Build import graph
    graph = build_import_graph(python_files)

    # Detect cycles
    cycles = detect_cycles(graph)

    if cycles:
        print("Circular imports detected:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  {i}. " + " -> ".join(cycle))
        return 1
    else:
        print("No circular imports detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
