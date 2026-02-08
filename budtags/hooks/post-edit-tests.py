#!/usr/bin/env python3
"""
PostToolUse Hook: Auto-Run Related Tests

After editing files, automatically runs the corresponding validation:
- app/**/*.php       → runs matching PHPUnit test in tests/Unit or tests/Feature
- tests/**/*Test.php → re-runs the edited test file itself
- resources/js/**/*.tsx|ts → runs TypeScript type-check (npx tsc --noEmit)
"""

import json
import os
import subprocess
import sys


def get_test_paths(file_path: str, project_dir: str) -> list[str]:
    """
    Map an app/ file to its potential test file paths.

    Returns list of possible test file paths.
    """
    test_paths = []

    # Remove leading project dir if present
    if file_path.startswith(project_dir):
        file_path = file_path[len(project_dir):].lstrip('/')

    # Only process app/**/*.php files
    if not file_path.startswith('app/') or not file_path.endswith('.php'):
        return test_paths

    # Get the relative path within app/
    relative_path = file_path[4:]  # Remove 'app/'

    # Generate test filename
    test_filename = relative_path.replace('.php', 'Test.php')

    # Check both Unit and Feature directories
    test_paths.append(os.path.join(project_dir, 'tests/Unit', test_filename))
    test_paths.append(os.path.join(project_dir, 'tests/Feature', test_filename))

    # Also check for Controller-specific test locations
    if 'Controllers/' in file_path:
        # app/Http/Controllers/ItemController.php → tests/Feature/ItemControllerTest.php
        controller_name = os.path.basename(file_path).replace('.php', 'Test.php')
        test_paths.append(os.path.join(project_dir, 'tests/Feature', controller_name))
        # Also check Http/Controllers subdirectory
        test_paths.append(os.path.join(project_dir, 'tests/Feature/Http/Controllers', controller_name))

    return test_paths


def run_tests(test_path: str, project_dir: str) -> tuple[int, str]:
    """
    Run PHPUnit tests for the given test file.

    Returns (return_code, output)
    """
    try:
        result = subprocess.run(
            ['php', 'artisan', 'test', test_path, '--compact'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        output = result.stdout + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, "Test execution timed out (120s limit)"
    except Exception as e:
        return 1, f"Error running tests: {e}"


def run_typecheck(file_path: str, project_dir: str) -> tuple[int, str]:
    """
    Run TypeScript type-check and filter to errors in the edited file only.

    Uses --skipLibCheck to ignore node_modules declaration errors.
    Returns (return_code, output) where output only contains errors
    from the edited file.
    """
    try:
        result = subprocess.run(
            ['npx', 'tsc', '--noEmit', '--skipLibCheck', '--pretty', 'false'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            return 0, ""

        # Filter output to only errors in the edited file
        relative = file_path
        if file_path.startswith(project_dir):
            relative = file_path[len(project_dir):].lstrip('/')

        relevant_lines = []
        for line in result.stdout.split('\n'):
            if line.startswith(relative):
                relevant_lines.append(line)

        if not relevant_lines:
            # Errors exist but not in the edited file — don't block
            return 0, ""

        return 1, '\n'.join(relevant_lines)

    except subprocess.TimeoutExpired:
        return 1, "TypeScript type-check timed out (120s limit)"
    except Exception as e:
        return 1, f"Error running type-check: {e}"


def is_typescript_file(file_path: str, project_dir: str) -> bool:
    """Check if the file is a TypeScript/TSX file under resources/js/."""
    relative = file_path
    if file_path.startswith(project_dir):
        relative = file_path[len(project_dir):].lstrip('/')

    return relative.startswith('resources/js/') and relative.endswith(('.ts', '.tsx'))


def is_test_file(file_path: str, project_dir: str) -> str | None:
    """
    Check if the file is a PHPUnit test file.

    Returns the test file path if it is, None otherwise.
    """
    relative = file_path
    if file_path.startswith(project_dir):
        relative = file_path[len(project_dir):].lstrip('/')

    if relative.startswith('tests/') and relative.endswith('Test.php'):
        return file_path

    return None


def handle_php_source(file_path: str, project_dir: str) -> None:
    """Handle editing an app/ PHP source file — find and run matching tests."""
    test_paths = get_test_paths(file_path, project_dir)

    if not test_paths:
        return

    # Find the first existing test file
    existing_test = None
    for test_path in test_paths:
        if os.path.exists(test_path):
            existing_test = test_path
            break

    if not existing_test:
        relative_path = file_path
        if file_path.startswith(project_dir):
            relative_path = file_path[len(project_dir):].lstrip('/')

        print(f"ℹ️ No test file found for {relative_path}")
        print(f"   Checked: {', '.join([p.replace(project_dir + '/', '') for p in test_paths[:2]])}")
        return

    return_code, output = run_tests(existing_test, project_dir)

    relative_test = existing_test
    if existing_test.startswith(project_dir):
        relative_test = existing_test[len(project_dir):].lstrip('/')

    if return_code != 0:
        result = {
            "decision": "block",
            "reason": f"Tests failed in {relative_test}:\n\n{output}\n\nPlease fix the failing tests before continuing."
        }
        print(json.dumps(result))
    else:
        print(f"✅ Tests passed: {relative_test}")


def handle_test_file(test_path: str, project_dir: str) -> None:
    """Handle editing a test file — re-run it to verify it passes."""
    return_code, output = run_tests(test_path, project_dir)

    relative_test = test_path
    if test_path.startswith(project_dir):
        relative_test = test_path[len(project_dir):].lstrip('/')

    if return_code != 0:
        result = {
            "decision": "block",
            "reason": f"Edited test is failing in {relative_test}:\n\n{output}\n\nPlease fix the test before continuing."
        }
        print(json.dumps(result))
    else:
        print(f"✅ Tests passed: {relative_test}")


def handle_typescript(file_path: str, project_dir: str) -> None:
    """Handle editing a TypeScript file — run type-check."""
    return_code, output = run_typecheck(file_path, project_dir)

    relative_path = file_path
    if file_path.startswith(project_dir):
        relative_path = file_path[len(project_dir):].lstrip('/')

    if return_code != 0:
        # Trim output to relevant errors (tsc can be verbose)
        lines = output.strip().split('\n')
        if len(lines) > 30:
            output = '\n'.join(lines[:30]) + f"\n... ({len(lines) - 30} more lines)"

        result = {
            "decision": "block",
            "reason": f"TypeScript errors after editing {relative_path}:\n\n{output}\n\nPlease fix the type errors before continuing."
        }
        print(json.dumps(result))
    else:
        print(f"✅ Type-check passed: {relative_path}")


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
        return

    # Get project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

    # Route to the appropriate handler
    test_file = is_test_file(file_path, project_dir)
    if test_file:
        handle_test_file(test_file, project_dir)
    elif is_typescript_file(file_path, project_dir):
        handle_typescript(file_path, project_dir)
    else:
        handle_php_source(file_path, project_dir)


if __name__ == "__main__":
    main()
