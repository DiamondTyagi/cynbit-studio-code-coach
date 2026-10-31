"""Run with:  pytest"""
from src.evaluator import evaluate
from src.missions import get_mission
from src.ml_model import predict_needs_help, train_model


def test_correct_solution_passes_all_tests():
    mission = get_mission("reverse_string")
    code = "def reverse_string(s):\n    return s[::-1]\n"
    result = evaluate(code, mission)
    assert result["passed"] == result["total"]


def test_wrong_solution_fails_some_tests():
    mission = get_mission("fizzbuzz")
    # forgot the FizzBuzz case
    code = (
        "def fizzbuzz(n):\n"
        "    if n % 3 == 0:\n        return 'Fizz'\n"
        "    if n % 5 == 0:\n        return 'Buzz'\n"
        "    return str(n)\n"
    )
    result = evaluate(code, mission)
    assert result["passed"] < result["total"]


def test_syntax_error_is_reported():
    mission = get_mission("reverse_string")
    result = evaluate("def reverse_string(s)\n    return s", mission)
    assert result["status"] == "syntax_error"


def test_infinite_loop_times_out():
    mission = get_mission("reverse_string")
    result = evaluate("def reverse_string(s):\n    while True:\n        pass\n", mission)
    assert result["status"] == "timeout"


def test_nested_loop_tip_for_find_duplicates():
    mission = get_mission("find_duplicates")
    code = (
        "def find_duplicates(nums):\n"
        "    out = []\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i + 1, len(nums)):\n"
        "            if nums[i] == nums[j] and nums[i] not in out:\n"
        "                out.append(nums[i])\n"
        "    return sorted(out)\n"
    )
    result = evaluate(code, mission)
    assert result["passed"] == result["total"]
    assert any("loop inside a loop" in tip for tip in result["tips"])


def test_print_instead_of_return_gives_tip():
    mission = get_mission("reverse_string")
    result = evaluate("def reverse_string(s):\n    print(s[::-1])\n", mission)
    assert any("prints" in tip for tip in result["tips"])


def test_model_gives_higher_risk_to_struggling_learner():
    model, _ = train_model()
    struggling = predict_needs_help(model, 10, 50, 0.1, 3, 3)
    doing_fine = predict_needs_help(model, 1, 3, 1.0, 0, 1)
    assert struggling > doing_fine
