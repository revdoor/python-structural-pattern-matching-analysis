from dataclasses import dataclass
from typing import List, Dict, Tuple
import ast


@dataclass
class Pattern:
    constructor: str
    args: List['Pattern']
    kwargs: Dict[str, 'Pattern'] = None

    @classmethod
    def wildcard(cls):
        return cls(constructor='_', args=[])

    @classmethod
    def wildcard_seq(cls):
        return cls(constructor='_seq', args=[])

    @classmethod
    def literal(cls, value):
        return cls(constructor=f'literal_{value}', args=[])

    @classmethod
    def or_pattern(cls, left: 'Pattern', right: 'Pattern'):
        return cls(constructor='or', args=[left, right])

    @classmethod
    def sequence(cls, elements: List['Pattern']):
        return cls(constructor=f'sequence_{len(elements)}', args=elements)

    @classmethod
    def map(cls, keys: List['Pattern'], values: List['Pattern']):
        if len(keys) != len(values):
            raise ValueError("Keys and values must have the same length")
        args = [item for pair in zip(keys, values) for item in pair]
        return cls(constructor=f'map_{len(keys)}', args=args)

    @classmethod
    def custom_class(cls, name: str, args: List['Pattern'], kwargs: Dict[str, 'Pattern']):
        return cls(constructor=f'custom_class_{name}', args=args, kwargs=kwargs)

    def __str__(self):
        if self.constructor == '_':
            return 'Wildcard()'

        elif self.constructor == '_seq':
            return 'WildcardSeq()'

        elif self.constructor.startswith('literal_'):
            return f'Literal({self.constructor[len("literal_"):]})'

        elif self.constructor == 'or':
            return f'Or({", ".join(str(arg) for arg in self.args)})'

        elif self.constructor.startswith('sequence_'):
            return f'Sequence({", ".join(str(arg) for arg in self.args)})'

        elif self.constructor.startswith('map_'):
            return f'Map({", ".join(str(arg) for arg in self.args)})'

        elif self.constructor.startswith('custom_class_'):
            name = self.constructor[len('custom_class_'):]

            args_str = ', '.join(str(arg) for arg in self.args)
            kwargs_str = ', '.join(f'{k}={v}' for k, v in self.kwargs.items()) if self.kwargs else ''

            return f'CustomClass({name}, {args_str}, {kwargs_str})'
        else:
            return f'{self.constructor}({", ".join(str(arg) for arg in self.args)})'


PatternMatrix = List[List[Pattern]]
PatternVector = List[Pattern]
