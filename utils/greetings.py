"""
Greeting utilities module.

This module provides functions for generating personalized greeting messages.
"""

from typing import Optional


def greet(name: Optional[str] = None) -> str:
    """
    Generate a personalized greeting message.

    Accepts a user's name as input and returns a personalized greeting
    formatted as "Hello, [Name]!". Handles edge cases gracefully.

    Args:
        name: The name of the person to greet. Can be None or empty string.

    Returns:
        A personalized greeting string formatted as "Hello, [Name]!".
        Returns "Hello, there!" for empty or null input.

    Edge Cases:
        - None/null input → "Hello, there!"
        - Empty string → "Hello, there!"
        - Whitespace-only → "Hello, there!"
        - Valid name → "Hello, [Name]!"

    Examples:
        >>> greet("Alice")
        'Hello, Alice!'

        >>> greet("")
        'Hello, there!'

        >>> greet(None)
        'Hello, there!'

        >>> greet("  Bob  ")
        'Hello, Bob!'
    """
    # Handle edge cases: null/None and empty string inputs
    if not name or not name.strip():
        return "Hello, there!"

    # Normalize the name by stripping whitespace
    normalized_name = name.strip()

    # Return personalized greeting formatted as "Hello, [Name]!"
    return f"Hello, {normalized_name}!"


if __name__ == "__main__":
    # Comprehensive test suite
    print("=" * 50)
    print("Testing greet() function - Task T-002")
    print("=" * 50)

    test_cases = [
        ("Alice", "Hello, Alice!", "Normal name input"),
        ("Bob Smith", "Hello, Bob Smith!", "Full name with space"),
        ("", "Hello, there!", "Empty string"),
        (None, "Hello, there!", "None/null input"),
        ("  ", "Hello, there!", "Whitespace only"),
        ("  Charlie  ", "Hello, Charlie!", "Name with surrounding whitespace"),
        ("\t\nDave\n\t", "Hello, Dave!", "Name with tabs and newlines"),
        ("X", "Hello, X!", "Single character name"),
    ]

    all_passed = True
    for i, (input_val, expected, description) in enumerate(test_cases, 1):
        result = greet(input_val)
        passed = result == expected
        all_passed = all_passed and passed

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\nTest {i}: {description}")
        print(f"  Input: {repr(input_val)}")
        print(f"  Expected: {expected}")
        print(f"  Got: {result}")
        print(f"  {status}")

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 50)
