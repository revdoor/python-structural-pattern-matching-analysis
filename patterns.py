from dataclasses import dataclass
from typing import List, Dict, Optional
import ast
from z3 import *
from union_var import UnionVar


@dataclass
class MatchPattern:
    constructor: str
    args: List['MatchPattern'] = None
    kwargs: Dict[str, 'MatchPattern'] = None
    var_name: Optional[str] = None

    @classmethod
    def empty(cls):
        return cls(constructor='empty', args=[])

    @classmethod
    def wildcard(cls):
        return cls(constructor='_', args=[])

    @classmethod
    def wildcard_seq(cls):
        return cls(constructor='_seq', args=[])

    @classmethod
    def var_binding(cls, var_name: str):
        return cls(constructor='var_binding', args=[], var_name=var_name)

    @classmethod
    def literal(cls, value):
        return cls(constructor=f'literal_{value}', args=[])

    @classmethod
    def or_pattern(cls, args: List['MatchPattern']):
        return cls(constructor='or', args=args)

    @classmethod
    def sequence(cls, elements: List['MatchPattern']):
        return cls(constructor=f'sequence_{len(elements)}', args=elements)

    @classmethod
    def map(cls, keys: List[str], values: List['MatchPattern']):
        if len(keys) != len(values):
            raise ValueError("Keys and values must have the same length")
        return cls(constructor=f'map_{len(keys)}', kwargs={k: v for k, v in zip(keys, values)})

    @classmethod
    def object(cls, name: str, args: List['MatchPattern'], kwargs: Dict[str, 'MatchPattern']):
        return cls(constructor=f'object_{name}', args=args, kwargs=kwargs)

    @property
    def is_empty(self):
        return self.constructor == 'empty'

    @property
    def is_wildcard(self):
        return self.constructor == '_' or self.constructor == 'var_binding'

    @property
    def is_wildcard_seq(self):
        return self.constructor == '_seq'

    @property
    def is_literal(self):
        return self.constructor.startswith('literal_')

    @property
    def is_or(self):
        return self.constructor == 'or'

    @property
    def is_sequence(self):
        return self.constructor.startswith('sequence_')

    @property
    def is_map(self):
        return self.constructor.startswith('map_')

    @property
    def is_object(self):
        return self.constructor.startswith('object_')

    @property
    def is_constructed(self):
        return self.is_literal or self.is_sequence

    @property
    def is_var_binding(self):
        return self.constructor == 'var_binding' and self.var_name is not None

    def __str__(self):
        if self.is_empty:
            return 'Empty()'

        elif self.is_wildcard and not self.is_var_binding:
            return 'Wildcard()'

        elif self.is_wildcard_seq:
            return 'WildcardSeq()'

        elif self.is_var_binding:
            return f'VarBinding({self.var_name})'

        elif self.is_literal:
            return f'Literal({self.constructor[len("literal_"):]})'

        elif self.is_or:
            return f'Or({", ".join(str(arg) for arg in self.args)})'

        elif self.is_sequence:
            return f'Sequence({", ".join(str(arg) for arg in self.args)})'

        elif self.is_map:
            items_str = ', '.join(f'{k}: {v}' for k, v in self.kwargs.items())
            return f'Map({items_str})'

        elif self.is_object:
            name = self.constructor[len('object_'):]

            args_str = ', '.join(str(arg) for arg in self.args) if self.args else ''
            kwargs_str = ', '.join(f'{k}={v}' for k, v in self.kwargs.items()) if self.kwargs else ''

            return f'Object({name}, {args_str}, {kwargs_str})'
        else:
            return f'{self.constructor}({", ".join(str(arg) for arg in self.args)})'

    def extend(self, other: List['MatchPattern']) -> List['MatchPattern']:
        if self.is_sequence:
            return self.args + other
        else:
            return [self] + other

    def convert_to_condition(self, union_var: UnionVar, union_vars: Optional[List[UnionVar]] = None) -> Bool:
        if self.is_empty:  # empty pattern, never matches
            return BoolVal(False)
        elif self.is_wildcard:  # wildcard matches anything
            return BoolVal(True)
        elif self.is_literal:  # literal matches specific value
            value = ast.literal_eval(self.constructor[len('literal_'):])
            return union_var == value
        elif self.is_or:
            compares = [arg.convert_to_condition(union_var, union_vars=union_vars) for arg in self.args]
            return Or(*compares)
        elif self.is_sequence:
            if union_vars is None or len(union_vars) != len(self.args):
                raise ValueError("Union variables must be provided for sequence patterns")
            compares = [arg.convert_to_condition(union_vars[i]) for i, arg in enumerate(self.args)]
            return And(*compares)
        else:
            raise NotImplementedError(f'Pattern conversion not implemented for {self.constructor} type')


class PatternVector:
    def __init__(self, patterns: List[MatchPattern], guard: Optional[ast.AST] = None):
        self.patterns = patterns
        self.guard = guard

    def __len__(self):
        return len(self.patterns)

    def __getitem__(self, index):
        return self.patterns[index]

    def __iter__(self):
        return iter(self.patterns)

    def __str__(self):
        return f'PatternVector({", ".join(str(pattern) for pattern in self.patterns)})' + \
                (f' with guard {ast.unparse(self.guard)}' if self.guard else '')

    @property
    def has_guard(self):
        return self.guard is not None

    @property
    def is_empty(self):
        return len(self.patterns) == 0


PatternMatrix = List[PatternVector]
