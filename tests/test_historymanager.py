import unittest
from unittest import mock
from datetime import datetime

from knosk.core import HistoryManager
from tests.util import SimpleForm


# stub for django model used previously
class DialogContext:
    pass


class HistoryManagerTest(unittest.TestCase):

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

    @unittest.skip('Dunno what to do with DialogContext model')
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

    @unittest.skip('Dunno what to do with DialogContext model')
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

    @unittest.skip('Dunno what to do with DialogContext model')
    def test_append_to_old_gen(self):
        with self.assertRaises(Exception, "Cannot modify read-only history"):
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

    @unittest.skip('Dunno what to do with DialogContext model')
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
