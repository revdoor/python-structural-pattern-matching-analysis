from dataclasses import dataclass
from typing import List
import ast


@dataclass
class Pattern:
    constructor: str
    args: List['Pattern']

    @classmethod
    def wildcard(cls):
        return cls(constructor='_', args=[])

    @classmethod
    def literal(cls, value):
        return cls(constructor=f'literal_{value}', args=[])

    @classmethod
    def or_pattern(cls, left: 'Pattern', right: 'Pattern'):
        return cls(constructor='or', args=[left, right])

    @classmethod
    def sequence(cls, elements: List['Pattern']):
        return cls(constructor=f'sequence_{len(elements)}', args=elements)


PatternMatrix = List[List[Pattern]]
PatternVector = List[Pattern]
