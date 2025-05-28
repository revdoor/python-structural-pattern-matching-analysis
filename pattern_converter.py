import ast
from patterns import *


def _extract_literal_value(node: ast.expr):
    if isinstance(node, ast.Constant):
        return node.value
    return ast.unparse(node)


def convert_pattern(pattern: ast.pattern) -> Pattern:
    if isinstance(pattern, ast.MatchValue):
        value = _extract_literal_value(pattern.value)
        return Pattern.literal(value)
    elif isinstance(pattern, ast.MatchSingleton):
        # MatchSingleton handles only None, True, or False
        value = pattern.value
        return Pattern.literal(value)
    elif isinstance(pattern, ast.MatchSequence):
        elements = [convert_pattern(pattern) for pattern in pattern.patterns]
        return Pattern.sequence(elements)
    elif isinstance(pattern, ast.MatchAs):
        if pattern.name is None:
            return Pattern.wildcard()
    else:
        # unknown pattern type
        raise ValueError(f"Unsupported pattern: {type(pattern)}")
