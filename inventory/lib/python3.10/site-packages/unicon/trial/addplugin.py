# addplugin.py
# Helper script to quickly create code for a new plugin.

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import yaml
import datetime
from jinja2 import Template

if __name__ == "__main__":
    for tf in ['templates/plugins.yaml', 'templates/unittest.yaml', 'templates/mock_data.yaml']:
        if not os.path.isfile(tf):
            print('Missing file {}'.format(tf))
            exit(1)

    plugin_name = input('plugin name: ')
    classname = plugin_name.capitalize()
    plugin_classname = input('plugin classname: ({}): '.format(classname))
    if not plugin_classname:
        plugin_classname = classname
    unicon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plugin_dir = os.path.join(unicon_dir, 'plugins', plugin_name)
    plugin_directory = input('plugin directory ({}): '.format(plugin_dir))
    if not plugin_directory:
        plugin_directory += plugin_dir
    state_name = input('state name: ')
    if state_name:
        prompt_re = input('{} prompt regex: '.format(state_name))
    else:
        state_name = 'STATE_NAME'
        prompt_re = 'PROMPT_REGEX'

    variables = {}
    variables['plugin_name'] = plugin_name
    variables['plugin_classname'] = plugin_classname
    variables['plugin_directory'] = plugin_directory
    variables['username'] = os.environ['USER']
    variables['state_name'] = state_name
    variables['prompt_re'] = prompt_re
    variables['year'] = datetime.datetime.now().year

    for v in variables:
        print("{}: {}".format(v, variables[v]))

    create_plugin = input('Create new plugin {}? (yes/no)'.format(plugin_name))
    if create_plugin == 'yes':
        if os.path.isdir(plugin_directory):
            print ('Plugin directory already exists')
            exit(1)
        else:
            os.mkdir(plugin_directory)

        jinja_template = Template(open('templates/plugins.yaml', 'r').read())
        plugin_templates = yaml.safe_load(jinja_template.render(variables))

        for module in plugin_templates:
            plugin_filename = os.path.join(plugin_directory, "{}.py".format(module))
            with open(plugin_filename, 'wb') as plugin_file:
                print('Creating {}.py as {}'.format(module, plugin_filename))
                plugin_file.write(plugin_templates[module].encode('utf-8'))

        jinja_template = Template(open('templates/unittest.yaml', 'r').read())
        unittest_templates = yaml.safe_load(jinja_template.render(variables))

        for module in unittest_templates:
            unittest_filename = os.path.join(unicon_dir, 'tests/unittest', "{}.py".format(module))
            with open(unittest_filename, 'wb') as unittest_file:
                print('Creating {}.py as {}'.format(module, unittest_filename))
                unittest_file.write(unittest_templates[module].encode('utf-8'))


        jinja_template = Template(open('templates/mock_data.yaml', 'r').read())
        mock_data_templates = yaml.safe_load(jinja_template.render(variables))

        for module in mock_data_templates:
            mock_data_directory = os.path.join(unicon_dir, 'mock/mock_data/{}'.format(plugin_name))
            if os.path.isdir(mock_data_directory):
                print ('Mock data directory already exists')
                exit(1)
            else:
                os.mkdir(mock_data_directory)
            mock_data_filename = os.path.join(mock_data_directory, "{}.yaml".format(module))
            with open(mock_data_filename, 'wb') as mock_data_file:
                print('Creating {}.yaml as {}'.format(module, mock_data_filename))
                mock_data_file.write(mock_data_templates[module].encode('utf-8'))
