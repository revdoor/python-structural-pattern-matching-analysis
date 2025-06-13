import z3


TYPE_INT = 0
TYPE_BOOL = 1
TYPE_STRING = 2


class UnionVar:
    def __init__(self, name: str):
        self.name = name

        self.type_var = z3.Int(f'{name}_type')
        self.int_var = z3.Int(f'{name}_int')
        self.bool_var = z3.Bool(f'{name}_bool')
        self.string_var = z3.String(f'{name}_string')

    def get_int_var(self):
        return self.int_var

    def get_bool_var(self):
        return self.bool_var

    def get_string_var(self):
        return self.string_var

    def get_type_var(self):
        return self.type_var

    def type_validity(self):
        return z3.Or(self.type_var == TYPE_INT,
                  self.type_var == TYPE_BOOL,
                  self.type_var == TYPE_STRING)

    def default_constraints(self):
        constraints = [self.type_validity(),
                       z3.Implies(self.type_var != TYPE_INT, self.int_var == 0),
                       z3.Implies(self.type_var != TYPE_BOOL, self.bool_var == False),
                       z3.Implies(self.type_var != TYPE_STRING, self.string_var == "")]

        return z3.And(*constraints)

    def __eq__(self, other):
        match other:
            case int():
                compare_condition = z3.And(self.type_var == TYPE_INT, self.int_var == other)
            case bool():
                compare_condition = z3.And(self.type_var == TYPE_BOOL, self.bool_var == other)
            case str():
                compare_condition = z3.And(self.type_var == TYPE_STRING, self.string_var == other)
            case _:
                raise ValueError(f"Unsupported type for comparison: {type(other)}")

        return compare_condition

    def __ne__(self, other):
        return z3.Not(self.__eq__(other))
