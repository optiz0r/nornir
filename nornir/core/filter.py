class F_OP_BASE(object):
    def __init__(self, op1: "F_OP_BASE", op2: "F_OP_BASE") -> None:
        self.op1 = op1
        self.op2 = op2

    def __and__(self, other: "F_OP_BASE") -> "F_OP_BASE":
        return AND(self, other)

    def __or__(self, other: "F_OP_BASE") -> "F_OP_BASE":
        return OR(self, other)

    def __repr__(self) -> str:
        return "( {} {} {} )".format(self.op1, self.__class__.__name__, self.op2)


class AND(F_OP_BASE):
    def __call__(self, obj: object) -> bool:
        return self.op1(obj) and self.op2(obj)


class OR(F_OP_BASE):
    def __call__(self, obj: object) -> bool:
        return self.op1(obj) or self.op2(obj)


class F(object):
    def __init__(self, **kwargs):
        self.filters = kwargs

    def __call__(self, obj: object) -> bool:
        return all(
            F._verify_rules(obj, k.split("__"), v) for k, v in self.filters.items()
        )

    def __and__(self, other: "F") -> bool:
        return AND(self, other)

    def __or__(self, other: "F") -> bool:
        return OR(self, other)

    def __invert__(self) -> bool:
        return NOT_F(**self.filters)

    def __repr__(self):
        return "<Filter ({})>".format(self.filters)

    @staticmethod
    def _verify_rules(data, rule, value):
        if len(rule) > 1:
            try:
                return F._verify_rules(data.get(rule[0], {}), rule[1:], value)
            except AttributeError:
                return False

        elif len(rule) == 1:
            operator = "__{}__".format(rule[0])
            if hasattr(data, operator):
                return getattr(data, operator)(value)

            elif hasattr(data, rule[0]):
                if callable(getattr(data, rule[0])):
                    return getattr(data, rule[0])(value)

                else:
                    return getattr(data, rule[0]) == value

            elif rule == ["in"]:
                return data in value
            elif rule == ["any"]:
                return any([x in data for x in value])
            elif rule == ["all"]:
                return all([x in data for x in value])
            else:
                return data.get(rule[0]) == value

        else:
            raise Exception(
                "I don't know how I got here:\n{}\n{}\n{}".format(data, rule, value)
            )


class NOT_F(F):
    def __call__(self, obj):
        return not any(
            F._verify_rules(obj, k.split("__"), v) for k, v in self.filters.items()
        )

    def __invert__(self):
        return F(**self.filters)

    def __repr__(self):
        return "<Filter NOT ({})>".format(self.filters)
