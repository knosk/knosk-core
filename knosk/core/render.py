import os
import logging
import random
import jinja2
LOG = logging.getLogger(__name__)


class TemplateRenderer:

    def __init__(self, app_path, tmpl_globals=None, tmpl_filters=None, default_tmpl_type='text'):
        self.__path = app_path
        self._tmpl_globals = tmpl_globals if tmpl_globals is not None else {}
        self._tmpl_filters = tmpl_filters if tmpl_filters is not None else {}
        self.default_tmpl_type = default_tmpl_type

    def _get_template_path(self, tmpl_name:str, tmpl_location, locale_name, tmpl_type, tmpl_custom_folders) -> str:
        """
            Find appropriate template
        """
        main_templates_folder = os.path.join(self.__path, tmpl_location)
        if not os.path.isdir(main_templates_folder):
            raise ValueError("Template path %s does not exist" % main_templates_folder)
        template_location = os.path.join(locale_name, tmpl_type, tmpl_name)
        default_template_location = os.path.join(locale_name, self.default_tmpl_type, tmpl_name)
        custom_templates = [tmpl_folder for tmpl_folder in tmpl_custom_folders if os.path.isdir(os.path.join(main_templates_folder, tmpl_folder, template_location))]

        full_templates_path = [] 
        if custom_templates:
            full_templates_path.append(os.path.join(main_templates_folder, custom_templates[0], template_location))
        full_templates_path.append(os.path.join(main_templates_folder, template_location))
        full_templates_path.append(os.path.join(main_templates_folder, default_template_location))

        available_templates = [tmpl_path for tmpl_path in full_templates_path if os.path.isdir(tmpl_path)]

        if not available_templates:
            raise ValueError("Full path template folders %s don't exist" % full_templates_path)

        full_path_to_templates = available_templates[0]

        template_names = [tmpl for tmpl in os.listdir(full_path_to_templates) if os.path.isfile(os.path.join(full_path_to_templates, tmpl)) and tmpl.endswith('.tmpl')]
        if not template_names:
            raise ValueError("Folder with templates %s is empty" % full_path_to_templates)

        template_path = os.path.join(full_path_to_templates, random.choice(template_names))
        return template_path

    def render(self, tmpl_name:str, tmpl_location='templates', locale_name='ru_RU', tmpl_type='text', tmpl_custom_folders=[], **kwargs) -> str:
        """Render results to string using jinja templates
            the idea is the following
            /template - main folder for templates
                |_ru_RU - main folder for RU locale
                    |_text - main folder for plain text templates it's default template type
                    |_facebook - facebook channel specific messages
                        |_ask_master - tmpl_name folder with templates for asking master templates will be picked up randomly from this folder
                            |_anyname.tmpl
                            |_anyothername.tmpl
                            |_whatevername.tmpl
                |_organization - it's tmpl_seek_folder
                    |_<id> - id for organization
                        |_ru_RU - main folder for RU locale
                            |_text - main folder for plain text templates it's default template type
                            |_facebook - facebook channel specific messages
                                |_ask_master - tmpl_name folder with templates for asking master templates will be picked up randomly from this folder
                                    |_anyname.tmpl
                                    |_anyothername.tmpl
                                    |_whatevername.tmpl
            so first priority has tmpl_custom_folders then locale_name, then tmpl_type then template name
        """
        tmpl_location = 'templates' if not tmpl_location else tmpl_location
        locale_name = 'ru_RU' if not locale_name else locale_name
        tmpl_type = 'text' if not tmpl_type else tmpl_type
        template_path = self._get_template_path(tmpl_name, tmpl_location, locale_name, tmpl_type, tmpl_custom_folders)
        with open(template_path, 'r') as tfile:
            tmpl_content = tfile.read()
            env = jinja2.Environment()
            env.globals.update(self._tmpl_globals)
            env.filters.update(self._tmpl_filters)
            tmpl = env.from_string(tmpl_content)
            return tmpl.render(**kwargs)
