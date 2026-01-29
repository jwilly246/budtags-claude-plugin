#!/usr/bin/env python3
"""
PostToolUse Hook: Auto-Run Related Tests

After editing PHP files in app/, automatically runs the corresponding test file.
Maps app/Services/MetrcApi.php → tests/Unit/Services/MetrcApiTest.php
Also checks tests/Feature/ for matching tests.
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


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    tool_result = input_data.get('tool_result', {})

    if not file_path:
        return

    # Get project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

    # Get potential test paths
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
        # No test file found - output informational message but don't block
        relative_path = file_path
        if file_path.startswith(project_dir):
            relative_path = file_path[len(project_dir):].lstrip('/')

        # Output as plain text (not JSON) so it shows in conversation
        print(f"ℹ️ No test file found for {relative_path}")
        print(f"   Checked: {', '.join([p.replace(project_dir + '/', '') for p in test_paths[:2]])}")
        return

    # Run the tests
    return_code, output = run_tests(existing_test, project_dir)

    # Get relative test path for display
    relative_test = existing_test
    if existing_test.startswith(project_dir):
        relative_test = existing_test[len(project_dir):].lstrip('/')

    if return_code != 0:
        # Tests failed - output decision to block with test output
        result = {
            "decision": "block",
            "reason": f"Tests failed in {relative_test}:\n\n{output}\n\nPlease fix the failing tests before continuing."
        }
        print(json.dumps(result))
    else:
        # Tests passed - output success message
        print(f"✅ Tests passed: {relative_test}")


if __name__ == "__main__":
    main()
