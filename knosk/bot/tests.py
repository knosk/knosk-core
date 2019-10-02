from django.test import TestCase
from bot import DialogForm, Flow, HistoryManager
from bot.fields import DialogField, GroupField, ListField, OverrideField
from models.models import Service, DialogContext
from unittest import mock
from datetime import datetime, time
from bot import TemplateRenderer


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


class DialogFormTest(TestCase):

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


class FlowManagerTest(TestCase):

    def test_simple_routing(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return (payload, ctx)
        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_two_handlers(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return (payload, ctx)

        @f.renderer("test")
        def r(flow, render_name, payload, ctx):
            return "render"

        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_calling_next_render(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return flow.render("somerender", payload, ctx)

        @f.renderer("somerender")
        def r(flow, render_name, payload, ctx):
            return "render"

        r = f.handle("test", {"a": "a"})

        assert r == "render"

    def test_simple_routing_with_positive_conditions(self):
        f = Flow()

        def condition(flow, parent, payload, ctx):
            return None

        @f.handler("test", conditions=[condition])
        def h(flow, render_name, payload, ctx):
            return (payload, ctx)

        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_negative_conditions(self):
        f = Flow()

        def condition(flow, parent, payload, ctx):
            return f.render("condition", payload, ctx)

        @f.renderer("condition")
        def r(flow, render_name, payload, ctx):
            return "render"

        @f.handler("test", conditions=[condition])
        def h(flow, render_name, payload, ctx):
            return (payload, ctx)

        r = f.handle("test", {"a": "a"})

        assert r == "render"

    def test_fallback(self):
        def a(ex, route_name, payload, ctx):
            self.assertEqual(route_name, "test")

        f = Flow(a)

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            raise Exception()

        f.handle("test", {"a": "a"})


class HistoryManagerTest(TestCase):

    def test_empty_history_from_json(self):
        json_data = {}
        dc = mock.Mock(DialogContext)
        dc.context = json_data
        h = HistoryManager(dc, parse=lambda e: e.context)
        self.assertEqual(len(h.all()), 0)

    def test_append_history(self):
        json_data = {}
        dc = mock.Mock(DialogContext)
        dc.context = json_data
        h = HistoryManager(dc, parse=lambda e: e.context)
        f = SimpleForm({'name': 'Vasia', 'some': [
                       '1'], 'f1': '22', 'f2': '33'})
        f.match()
        f.suggest()
        h.append('test', f, 'testing')
        self.assertEqual(len(h.all()), 1)
        self.assertEqual(f, h.first().form)

    def test_append_history_compare_deserialize(self):
        def on_save(hist, d_context):
            d_context.context = hist.to_json()
            d_context.save()

        json_data = {}
        dc = mock.Mock(DialogContext)
        dc.context = json_data
        h = HistoryManager(dc, parse=lambda e: e.context, on_save=on_save)
        f = SimpleForm({'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
        f.match()
        f.suggest()
        h.append('test', f, 'testing')
        self.assertEqual(len(h.all()), 1)
        h2 = HistoryManager(dc, parse=lambda e: e.context, on_save=on_save)
        self.assertEqual(h.first().name, h2.first().name)
        self.assertEqual(h2.first().form.get('name').get_value(), ['TTT'])

    def test_history_with_old_gen(self):
        def on_save(hist, d_context):
            d_context.context = hist.to_json()
            d_context.save()

        json_data = {}
        dc = mock.Mock(DialogContext)
        dc.context = json_data

        json_data_old = [{'timestamp': datetime.now(), 'name': 'a'}, {'timestamp': datetime.now(), 'name': 'b'}]
        dc_old = mock.Mock(DialogContext)
        dc_old.context = json_data_old

        h = HistoryManager(dc, dc_old, parse=lambda e: e.context, on_save=on_save)
        f = SimpleForm({'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
        f.match()
        f.suggest()
        h.append('test', f, 'testing')
        self.assertEqual(len(h.all()), 1)
        self.assertEqual(len(h.old.all()), 2)

        h2 = HistoryManager(dc, parse=lambda e: e.context, on_save=on_save)
        self.assertEqual(h.first().name, h2.first().name)
        self.assertEqual(h2.first().form.get('name').get_value(), ['TTT'])

    def test_append_to_old_gen(self):
        with self.assertRaisesMessage(Exception, "Cannot modify read-only history"):
            def on_save(hist, d_context):
                d_context.context = hist.to_json()
                d_context.save()

            json_data = {}
            dc = mock.Mock(DialogContext)
            dc.context = json_data

            json_data_old = [{'timestamp': datetime.now(), 'name': 'a'}, {'timestamp': datetime.now(), 'name': 'b'}]
            dc_old = mock.Mock(DialogContext)
            dc_old.context = json_data_old

            h = HistoryManager(dc, dc_old, parse=lambda e: e.context, on_save=on_save)
            f = SimpleForm({'name': 'Vasia', 'some': ['1'], 'f1': '22', 'f2': '33'})
            h.old.append('test', f, 'testing')

    def test_with_db(self):
        def on_save(hist, d_context):
            d_context.context = hist.to_json()
            d_context.save()

        dc = DialogContext()
        dc.save()
        ndc = DialogContext.objects.get(id=dc.id)
        h = HistoryManager(dc, parse=lambda e: e.context, on_save=on_save)
        d = datetime.now()
        t = d.time()
        f = SimpleForm({'name': 'Vasia', 'some': [
                       '1'], 'f1': '22', 'f2': '33'})
        f.match()
        f.suggest()
        h.append('test', f, 'testing')
        self.assertEqual(len(h.all()), 1)
        ndc2 = DialogContext.objects.get(id=dc.id)
        h2 = HistoryManager(ndc2, parse=lambda e: e.context, on_save=on_save)
        self.assertEqual(h.first().name, h2.first().name)
        self.assertEqual(h2.first().form.get('name').get_value(), ['TTT'])

class RenderTest(TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_applocation')
        isdir_mock.return_value=True
        isfile_mock.return_value=True
        listdir_mock.return_value=['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content'
        f = mock.MagicMock()
        f.read.return_value= tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test')
        self.assertEqual(result, tmpl_content)


    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render2(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_applocation')
        isdir_mock.return_value=True
        isfile_mock.return_value=True
        listdir_mock.return_value=['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content {{a}}'
        f = mock.MagicMock()
        f.read.return_value= tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', a='1')
        self.assertEqual(result, 'Test template content 1')


    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render3(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_applocation', tmpl_globals={'x':'RRR'})
        isdir_mock.return_value=True
        isfile_mock.return_value=True
        listdir_mock.return_value=['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value= tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', a='1')
        self.assertEqual(result, 'Test template content 1-RRR')


    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render4(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_applocation', tmpl_globals={'x':'RRR'})
        isdir_mock.return_value=True
        isfile_mock.return_value=True
        listdir_mock.return_value=['1.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value= tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', locale_name="en_US", a='1')
        open_mock.assert_called_with('test_applocation/templates/en_US/text/test/1.tmpl', 'r')
        self.assertEqual(result, 'Test template content 1-RRR')

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render5(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_applocation', tmpl_globals={'x':'RRR'})
        isdir_mock.return_value=True
        isfile_mock.return_value=True
        listdir_mock.return_value=['1.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value= tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', locale_name="en_US", tmpl_type='facebook', tmpl_custom_folders=['organizations/1'], a='1')
        open_mock.assert_called_with('test_applocation/templates/organizations/1/en_US/facebook/test/1.tmpl', 'r')
        self.assertEqual(result, 'Test template content 1-RRR')
