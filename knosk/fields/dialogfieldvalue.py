class DialogFieldValue:

    def __init__(self, value: list):
        self._value = value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        if other:
            return self.value == other.value
        return False

    def __str__(self):
        return "%s" % self.value


class EmptyDialogFieldValue(DialogFieldValue):

    def __init__(self, value: list):
        super(EmptyDialogFieldValue, self).__init__([])


class SingleDialogFieldValue(DialogFieldValue):

    def __init__(self, value: list):
        if isinstance(value, list) and len(value) != 1:
            raise ValueError("Value %s should be single" % value)
        if isinstance(value, list):
            super(SingleDialogFieldValue, self).__init__(value)
        else:
            super(SingleDialogFieldValue, self).__init__([value])

    @property
    def value(self):
        return self._value


class MultiDialogFieldValue(DialogFieldValue):
    pass


class SuggestedListFieldValue(DialogFieldValue):
    pass


class FieldValue:

    @staticmethod
    def create(value: list, is_suggest=False):
        if value and isinstance(value, list) and len(value) > 1:
            if not is_suggest:
                return MultiDialogFieldValue(value)
            else:
                return SuggestedListFieldValue(value)
        elif value:
            return SingleDialogFieldValue(value)
        else:
            return EmptyDialogFieldValue([])

    @staticmethod
    def create_suggested(value: list):
        return FieldValue.create(value, is_suggest=True)

    @staticmethod
    def empty():
        return EmptyDialogFieldValue([])

    @staticmethod
    def is_empty(field_value: DialogFieldValue):
        return isinstance(field_value, EmptyDialogFieldValue)

    @staticmethod
    def is_not_empty(field_value: DialogFieldValue):
        return not FieldValue.is_empty(field_value)

    @staticmethod
    def is_single(field_value: DialogFieldValue):
        return isinstance(field_value, SingleDialogFieldValue)

    @staticmethod
    def is_multy(field_value: DialogFieldValue):
        return isinstance(field_value, MultiDialogFieldValue)

    @staticmethod
    def is_suggested(field_value: DialogFieldValue):
        return isinstance(field_value, SuggestedListFieldValue)
