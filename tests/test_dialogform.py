import unittest

from knosk.fields import DialogField, GroupField, ListField, OverrideField
from knosk.core import DialogForm
from tests.util import SimpleForm


class DialogFormTest(unittest.TestCase):

    def test_simple_form_without_matches(self):
        class SimpleForm(DialogForm):
            name = DialogField(source='name')
            lastname = DialogField(source='some')

            class Meta:
                fields = ('name', 'lastname')
        form = SimpleForm({'name': 'Vasia'})
        self.assertEqual(form.get('name').origin.value, ['Vasia'])

    def test_simple_form_with_matcher(self):
        def matcher(value, form):
            return "TTT"

        class SimpleForm(DialogForm):
            name = DialogField(source='name', matcher=matcher)
            lastname = DialogField(source='some')

            class Meta:
                fields = ('name', 'lastname')
        form = SimpleForm({'name': 'Vasia', 'some': '1'})
        form.match()
        self.assertEqual(form.get('name').get_value(), ['TTT'])

    def test_simple_form_with_suggester(self):
        def suggester(field, form):
            return ["TTT", "HHH"]

        class SimpleForm(DialogForm):
            name = DialogField(source='name', suggesters=[suggester])
            lastname = DialogField(source='some')

            class Meta:
                fields = ('name', 'lastname')
        form = SimpleForm({'name': 'Vasia', 'some': '1'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('name').get_value(), ['TTT', 'HHH'])

    def test_simple_form_with_suggester_and_chooser(self):
        def suggester(field, form):
            return ["TTT", "HHH"]

        def chooser(value):
            return [value[0]]

        class SimpleForm(DialogForm):
            name = DialogField(
                source='name',
                suggesters=[suggester],
                choosers=[chooser])
            lastname = DialogField(source='some')

            class Meta:
                fields = ('name', 'lastname')
        form = SimpleForm({'name': 'Vasia', 'some': '1'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('name').get_value(), ['TTT'])

    def test_simple_form_with_group(self):
        def suggester(field, form):
            return ["TTT", "HHH"]

        def suggester2(field, form):
            return ["3", "1"]

        def chooser(value):
            return [value[0]]

        class SimpleForm(DialogForm):
            name = DialogField(
                source='name',
                suggesters=[suggester],
                choosers=[chooser])
            lastname = DialogField(source='some')
            gp = GroupField(
                source=[
                    DialogField(
                        source='f1', suggesters=[suggester2]), DialogField(
                        source='f2')])

            class Meta:
                fields = ('name', 'lastname', 'gp')
        form = SimpleForm({'name': 'Vasia', 'some': '1', 'f2': '33'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('name').get_value(), ['TTT'])
        self.assertEqual(form.get('gp').get_value(), [])
        self.assertEqual(form.get('gp').origin.value, ['33'])

    def test_simple_form_with_group2(self):
        def suggester(field, form):
            return ["TTT", "HHH"]

        def suggester2(field, form):
            return ["3", "1"]

        def chooser(value):
            return [value[0]]

        def chooser2(value):
            return [value[0]]

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

            class Meta:
                fields = ('name', 'gp')
        form = SimpleForm(
            {'name': 'Vasia', 'some': '1', 'f1': '22', 'f2': '33'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('name').get_value(), ['TTT'])
        self.assertEqual(form.get('gp').get_value(), ['3'])

    def test_simple_form_with_list(self):
        def matcher(field, form):
            return ['1', '3']

        def suggester(field, form):
            return ["TTT", "HHH"]

        def suggester2(field, form):
            return ["3", "1"]

        def chooser(value):
            return [value[0]]

        def chooser2(value):
            return [value[0]]

        class SimpleForm(DialogForm):
            lastnames = ListField(source='some', matcher=matcher)

            class Meta:
                fields = ('lastnames',)
        form = SimpleForm(
            {'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('lastnames').get_value(), ['1', '3'])

    def test_form_validate(self):
        def matcher(field, form):
            return ['1', '3']

        class SimpleForm(DialogForm):
            lastnames = ListField(source='some', matcher=matcher)

            class Meta:
                fields = ('lastnames',)

            def validate(self, dialog):
                if not dialog:
                    raise ValueError("Need to pass dialog")
                if self.get('lastnames').get_value() != ['1', '3']:
                    raise ValueError("lastnames should be ['1','3']")

        form = SimpleForm(
            {'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('lastnames').get_value(), ['1', '3'])
        form.validate(dialog={"1": "1"})

    def test_form_serializer(self):
        form = SimpleForm(
            {'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
        form.match()
        form.suggest()
        self.assertEqual(form.get('lastnames').get_value(), ['1', '3'])
        self.assertEqual(form.get('name').get_value(), ['TTT'])
        self.assertEqual(form.get('gp').get_value(), ['3'])
        result = form.serialize()
        new_form = DialogForm.get_form(result)
        self.assertEqual(
            form.get('lastnames').get_value(),
            new_form.get('lastnames').get_value())
        self.assertEqual(
            form.get('name').get_value(),
            new_form.get('name').get_value())
        self.assertEqual(
            form.get('gp').get_value(),
            new_form.get('gp').get_value())

    def test_form_overriders(self):
        def suggester3(field, form):
            return ['12', '34', 55]
        form = SimpleForm({'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'}, overrides=[
                          OverrideField(source='name', suggesters=[suggester3])])
        form.match()
        form.suggest()
        self.assertEqual(form.get('lastnames').get_value(), ['1', '3'])
        self.assertEqual(form.get('name').get_value(), ['12'])
        self.assertEqual(form.get('gp').get_value(), ['3'])
