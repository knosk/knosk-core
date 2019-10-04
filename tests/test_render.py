import unittest
from unittest import mock

from knosk.core import TemplateRenderer


class RenderTest(unittest.TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_application')
        isdir_mock.return_value = True
        isfile_mock.return_value = True
        listdir_mock.return_value = ['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content'
        f = mock.MagicMock()
        f.read.return_value = tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test')
        self.assertEqual(result, tmpl_content)

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render2(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_application')
        isdir_mock.return_value = True
        isfile_mock.return_value = True
        listdir_mock.return_value = ['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content {{a}}'
        f = mock.MagicMock()
        f.read.return_value = tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', a='1')
        self.assertEqual(result, 'Test template content 1')

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render3(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_application', tmpl_globals={'x': 'RRR'})
        isdir_mock.return_value = True
        isfile_mock.return_value = True
        listdir_mock.return_value = ['1.tmpl', '2.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value = tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', a='1')
        self.assertEqual(result, 'Test template content 1-RRR')

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render4(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_application', tmpl_globals={'x': 'RRR'})
        isdir_mock.return_value = True
        isfile_mock.return_value = True
        listdir_mock.return_value = ['1.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value = tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test', locale_name="en_US", a='1')
        open_mock.assert_called_with('test_application/templates/en_US/text/test/1.tmpl', 'r')
        self.assertEqual(result, 'Test template content 1-RRR')

    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    @mock.patch('os.listdir')
    @mock.patch('os.path.isdir')
    def test_render5(self, isdir_mock, listdir_mock, open_mock, isfile_mock):
        renderer = TemplateRenderer('test_application', tmpl_globals={'x': 'RRR'})
        isdir_mock.return_value = True
        isfile_mock.return_value = True
        listdir_mock.return_value = ['1.tmpl']

        tmpl_content = 'Test template content {{a}}-{{x}}'
        f = mock.MagicMock()
        f.read.return_value = tmpl_content

        open_mock.return_value.__enter__.return_value = f

        result = renderer.render('test',
                                 locale_name="en_US",
                                 tmpl_type='facebook',
                                 tmpl_custom_folders=['organizations/1'], a='1')
        open_mock.assert_called_with('test_application/templates/organizations/1/en_US/facebook/test/1.tmpl', 'r')
        self.assertEqual(result, 'Test template content 1-RRR')
