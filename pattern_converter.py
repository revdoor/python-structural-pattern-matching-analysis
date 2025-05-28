import ast
from patterns import *
from todo_error import TodoError


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
        if pattern.pattern is None:
            # MatchAs without a pattern is either a wildcard or a variable binding
            # When analyzing, the variable binding can be treated as a wildcard
            return Pattern.wildcard()
        return convert_pattern(pattern.pattern)
    else:
        # unknown pattern type
        raise ValueError(f"Unsupported pattern: {type(pattern)}")
