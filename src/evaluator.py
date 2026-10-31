"""
evaluator.py

Checks a student's code in 3 steps:
  1. Syntax check      -> is the code even valid Python?
  2. Static checks     -> look at the code's structure with the `ast` module (no running)
  3. Run the tests     -> run the code on the mission's test cases in a SEPARATE process
                          with a time limit, so an infinite loop cannot freeze the app.

NOTE: This is a demo. For real students on a server, the code should run inside a
locked-down sandbox (for example a Docker container with no network).
"""

import ast
import json
import subprocess
import sys

TIME_LIMIT_SECONDS = 5

# This small program is run in a new Python process.
# It reads the student's code + tests from stdin and prints the results as JSON.
RUNNER = """
import sys, json, io, contextlib

data = json.loads(sys.stdin.read())
namespace = {}
results = []

try:
    # student's print() output is thrown away so it does not mix with our JSON
    with contextlib.redirect_stdout(io.StringIO()):
        exec(data["code"], namespace)
    func = namespace[data["func"]]
except Exception as e:
    print("RESULT:" + json.dumps({"setup_error": str(e)}))
    sys.exit(0)

for args, expected in data["tests"]:
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            got = func(*args)
        got = json.loads(json.dumps(got))   # turns tuples into lists, etc.
        results.append({"args": args, "expected": expected, "got": got, "passed": got == expected})
    except Exception as e:
        results.append({"args": args, "expected": expected, "got": "Error: " + str(e), "passed": False})

print("RESULT:" + json.dumps({"results": results}))
"""


def check_syntax(code):
    """Return None if the code is valid, otherwise a friendly error message."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as error:
        return "Syntax error on line " + str(error.lineno) + ": " + str(error.msg)


def static_checks(code, mission):
    """
    Look at the structure of the code (without running it) and return a list of tips.
    """
    tips = []
    tree = ast.parse(code)

    # Did the student define the function with the right name?
    function_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    names = [f.name for f in function_nodes]
    if mission["function_name"] not in names:
        tips.append("I could not find a function named '" + mission["function_name"] + "'. Check the spelling.")
        return tips  # the other checks need the function, so stop here

    my_function = function_nodes[names.index(mission["function_name"])]

    # print() used but nothing is returned?
    uses_print = any(
        isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"
        for n in ast.walk(my_function)
    )
    has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(my_function))
    if uses_print and not has_return:
        tips.append("Your function prints a value but does not return it. Tests need 'return'.")
    if not has_return:
        tips.append("Your function never returns a value, so it gives back None.")

    # Loop inside a loop? (can be slow for big inputs)
    if mission["level"] >= 2 and has_nested_loop(my_function):
        tips.append("You have a loop inside a loop. It works for small lists but gets slow for big ones. "
                    "Can a set or dictionary help?")

    return tips


def has_nested_loop(function_node):
    """True if any for/while loop contains another for/while loop."""
    for node in ast.walk(function_node):
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if child is not node and isinstance(child, (ast.For, ast.While)):
                    return True
    return False


def run_tests(code, mission):
    """
    Run the student's code on the mission tests.
    Returns a dictionary: {"status": ..., "results": [...], "passed": n, "total": n}
    status is one of: "ok", "timeout", "error"
    """
    payload = json.dumps({
        "code": code,
        "func": mission["function_name"],
        "tests": mission["tests"],
    })

    total = len(mission["tests"])
    try:
        completed = subprocess.run(
            [sys.executable, "-c", RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            timeout=TIME_LIMIT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "results": [], "passed": 0, "total": total,
                "message": "Your code took longer than " + str(TIME_LIMIT_SECONDS)
                           + " seconds. Is there an infinite loop?"}

    # find our marker line in the output
    marker_lines = [line for line in completed.stdout.splitlines() if line.startswith("RESULT:")]
    if not marker_lines:
        return {"status": "error", "results": [], "passed": 0, "total": total,
                "message": "Your code crashed: " + completed.stderr[-300:]}

    data = json.loads(marker_lines[-1][len("RESULT:"):])
    if "setup_error" in data:
        return {"status": "error", "results": [], "passed": 0, "total": total,
                "message": "Your code could not be loaded: " + data["setup_error"]}

    results = data["results"]
    passed = sum(1 for r in results if r["passed"])
    return {"status": "ok", "results": results, "passed": passed, "total": total, "message": ""}


def evaluate(code, mission):
    """Run all 3 steps and return everything the app needs to show."""
    syntax_error = check_syntax(code)
    if syntax_error:
        return {"status": "syntax_error", "message": syntax_error, "tips": [],
                "results": [], "passed": 0, "total": len(mission["tests"])}

    tips = static_checks(code, mission)
    outcome = run_tests(code, mission)
    outcome["tips"] = tips
    return outcome
