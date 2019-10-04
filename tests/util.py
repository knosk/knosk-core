from knosk.fields import DialogField, GroupField, ListField
from knosk.core import DialogForm


# This things was needed to move out cause of serialize/deserialize testing
def suggester(field, form):
    return ["TTT", "HHH"]


def suggester2(field, form):
    return ["3", "1"]


def chooser(value):
    return [value[0]]


def chooser2(value):
    return [value[0]]


def matcher(field, form):
    return ['1', '3']


class SimpleForm(DialogForm):
    name = DialogField(
        source='name',
        suggesters=[suggester],
        choosers=[chooser])
    gp = GroupField(
        source=[
            DialogField(
                source='f1',
                suggesters=[suggester2],
                choosers=[chooser2]),
            DialogField(
                source='f2')])
    lastnames = ListField(source='some', matcher=matcher)

    class Meta:
        fields = ('name', 'gp', 'lastnames')
