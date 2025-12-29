"""
Helper utility functions
"""

import re
from typing import Optional, Tuple


def safe_float(value) -> Optional[float]:
    """Safely convert value to float, returning None if invalid."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_simple_math(query: str) -> Optional[str]:
    """
    Calculate simple arithmetic from natural language queries.
    Handles: addition, subtraction, multiplication, division
    Examples: "what is 7 into 5", "5 plus 3", "10 divided by 2"
    """
    query_lower = query.lower().strip()
    
    # Pattern for "X operation Y" style questions
    # Matches: "what is 7 into 5", "calculate 10 plus 3", etc.
    patterns = [
        # Multiplication patterns
        (r'(\d+(?:\.\d+)?)\s*(?:into|times|multiplied by|x|\*)\s*(\d+(?:\.\d+)?)', '*'),
        # Addition patterns  
        (r'(\d+(?:\.\d+)?)\s*(?:plus|\+|add(?:ed)? to)\s*(\d+(?:\.\d+)?)', '+'),
        # Subtraction patterns
        (r'(\d+(?:\.\d+)?)\s*(?:minus|-|subtract(?:ed)?|less)\s*(\d+(?:\.\d+)?)', '-'),
        # Division patterns
        (r'(\d+(?:\.\d+)?)\s*(?:divided by|over|\/)\s*(\d+(?:\.\d+)?)', '/'),
    ]
    
    for pattern, operator in patterns:
        match = re.search(pattern, query_lower)
        if match:
            try:
                num1 = float(match.group(1))
                num2 = float(match.group(2))
                
                if operator == '*':
                    result = num1 * num2
                    op_word = "multiplied by"
                elif operator == '+':
                    result = num1 + num2
                    op_word = "plus"
                elif operator == '-':
                    result = num1 - num2
                    op_word = "minus"
                elif operator == '/':
                    if num2 == 0:
                        return "Cannot divide by zero!"
                    result = num1 / num2
                    op_word = "divided by"
                else:
                    continue
                
                # Format result nicely (remove .0 for whole numbers)
                if result == int(result):
                    result_str = str(int(result))
                else:
                    result_str = str(result)
                
                return f"{num1} {op_word} {num2} equals {result_str}."
                
            except (ValueError, ZeroDivisionError):
                continue
    
    return None
