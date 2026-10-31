"""
missions.py

A "mission" is one small coding problem, like the missions in Cynbit Studio.
Each mission has:
  - the function name the student must write
  - test cases: (list of arguments, expected answer)
  - 3 hints, from vague to very specific
"""

MISSIONS = [
    {
        "id": "reverse_string",
        "title": "Reverse a string",
        "level": 1,
        "description": "Write a function reverse_string(s) that returns the string s written backwards.",
        "function_name": "reverse_string",
        "starter": "def reverse_string(s):\n    # write your code here\n    pass\n",
        "tests": [
            (["hello"], "olleh"),
            (["a"], "a"),
            ([""], ""),
            (["Cynbit"], "tibnyC"),
        ],
        "hints": [
            "Think about how you would read the word from the last letter to the first.",
            "A for loop can go through the string. Build a new string by adding each letter to the FRONT of it.",
            "Python shortcut: s[::-1] gives the reversed string (slicing with a step of -1).",
        ],
    },
    {
        "id": "fizzbuzz",
        "title": "FizzBuzz for one number",
        "level": 1,
        "description": (
            "Write fizzbuzz(n). Return 'FizzBuzz' if n is divisible by 3 and 5, "
            "'Fizz' if only by 3, 'Buzz' if only by 5, otherwise return n as a string."
        ),
        "function_name": "fizzbuzz",
        "starter": "def fizzbuzz(n):\n    # write your code here\n    pass\n",
        "tests": [
            ([3], "Fizz"),
            ([5], "Buzz"),
            ([15], "FizzBuzz"),
            ([7], "7"),
            ([30], "FizzBuzz"),
        ],
        "hints": [
            "The % operator gives the remainder. n % 3 == 0 means n is divisible by 3.",
            "Order matters! Check the 'divisible by both' case FIRST, before the single cases.",
            "Check n % 15 == 0 first, then n % 3, then n % 5, and finally return str(n).",
        ],
    },
    {
        "id": "find_duplicates",
        "title": "Find duplicates in a list",
        "level": 2,
        "description": (
            "Write find_duplicates(nums). Return a sorted list of the numbers that appear "
            "more than once in nums. Each duplicate should appear only once in the answer."
        ),
        "function_name": "find_duplicates",
        "starter": "def find_duplicates(nums):\n    # write your code here\n    pass\n",
        "tests": [
            ([[1, 2, 3, 2, 1]], [1, 2]),
            ([[1, 2, 3]], []),
            ([[]], []),
            ([[5, 5, 5, 5]], [5]),
            ([[4, 1, 4, 3, 3, 9]], [3, 4]),
        ],
        "hints": [
            "You need to remember which numbers you have already seen.",
            "Use a dictionary (or a set) to count / remember numbers while looping once over the list.",
            "Keep a 'seen' set and a 'dups' set. If a number is already in seen, add it to dups. Return sorted(dups).",
        ],
    },
    {
        "id": "two_sum",
        "title": "Two Sum",
        "level": 3,
        "description": (
            "Write two_sum(nums, target). Find two different positions i < j such that "
            "nums[i] + nums[j] == target, and return [i, j]. Exactly one answer exists."
        ),
        "function_name": "two_sum",
        "starter": "def two_sum(nums, target):\n    # write your code here\n    pass\n",
        "tests": [
            ([[2, 7, 11, 15], 9], [0, 1]),
            ([[3, 2, 4], 6], [1, 2]),
            ([[3, 3], 6], [0, 1]),
            ([[1, 5, 8, 12, 20], 28], [2, 4]),
        ],
        "hints": [
            "The brute-force way is to check every pair. That works, but is slow for big lists.",
            "While looping, ask: 'have I already seen the number I need (target - current)?'",
            "Use a dictionary {number: index}. For each x, check if target - x is in the dictionary before adding x.",
        ],
    },
]


def get_mission(mission_id):
    """Return the mission dictionary with the given id."""
    for mission in MISSIONS:
        if mission["id"] == mission_id:
            return mission
    raise ValueError("Unknown mission: " + mission_id)
