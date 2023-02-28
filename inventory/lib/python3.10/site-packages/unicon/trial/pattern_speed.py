""" Check processing speed of plugin regex patterns

This scripts loads the pattern classes of all the plugin modules in Unicon,
generates a random text and checks the processing time to match a pattern.

Patterns with processing times > 2ms will be listed as slow patterns.

"""

__author__ = "Dave Wapstra"
__email__ = "dwapstra@cisco.com"


import os
import re
import random
import string
import inspect
import datetime
import importlib
import unicon.plugins as plugins
from unicon.core.pluginmanager import PluginManager


def find_files(current_dir, filename_pattern, file_extension):
    target_files=[]
    for subdir, dirs, files in os.walk(current_dir):
        for file in files:
            if re.search('\.{}$'.format(file_extension), file) or file_extension=="*":
                if re.match(filename_pattern, file):
                    target_files.append(os.path.join(subdir,file))
    return target_files

def random_string(length):
    return ''.join (random.choice (string.ascii_letters) for ii in range (length + 1))

def random_lines(num_lines, line_length=80):
    random_text = ""
    for x in range(num_lines):
        random_text += random_string(line_length) + '\n'
    return random_text

def find_pattern_modules(plugin_names):
    pattern_modules = {}

    for plugin_name in plugin_names:
        plugin = getattr(plugins, plugin_name)
        plugin_dir = os.path.dirname(plugin.__file__)
        pattern_module_files = find_files(plugin_dir, '(service_)?pattern', 'py')
        for pattern_file in pattern_module_files:
            relative_filename = re.sub('.*/plugins/', '', pattern_file)
            pattern_module_name = relative_filename.replace('.py', '').replace('/','.')
            pattern_module = importlib.import_module("unicon.plugins.{}".format(pattern_module_name))
            plugin_module_name = os.path.dirname(relative_filename).replace('/', '.')
            if plugin_module_name in pattern_modules:
                pattern_modules[plugin_module_name].append(pattern_module)
            else:
                pattern_modules[plugin_module_name] = []
                pattern_modules[plugin_module_name].append(pattern_module)

    return pattern_modules

def find_moduleclasses(module, plugin_name):
    class_names = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if plugin_name in str(obj):
                #print (name, obj)
                class_names.append(name)

    return class_names

def check_processing_times(patterns):
    slow_patterns = {}

    random_text = random_lines(200)

    for p in sorted(patterns):
        print("Pattern: {}, ".format(p), end="", flush=True)
        regex = patterns[p]
        start_time = datetime.datetime.now()
        m = re.search(regex,random_text)
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        us = elapsed_time.microseconds
        print("us: {}".format(us))
        if us > 2000:
            slow_patterns[p] = us

    return slow_patterns


plugin_names = sorted(PluginManager().supported_os)
pattern_modules = find_pattern_modules(plugin_names)

slow_patterns = {}
for plugin_name in pattern_modules:
    slow_patterns[plugin_name] = {}
    for pattern_module in pattern_modules[plugin_name]:
        classes = find_moduleclasses(pattern_module, plugin_name)
        for class_name in classes:
            # assuming that patterns and service_patterns don't have duplicate class names
            slow_patterns[plugin_name][class_name] = {}
            pattern_class = getattr(pattern_module, class_name)
            patterns = pattern_class().__dict__
            print('*' * 10, "checking {} {} ".format(plugin_name, class_name), '*' * 10)
            slow_patterns[plugin_name][class_name].update(check_processing_times(patterns))

print('#'*40)
print('# Slow patterns (shown below if any)')
print('#'*40)
print("{:<20} {:<25} {:<35} {:>10}".format("Plugin", "Class", "Pattern", "Time(us)"))
for plugin_name in sorted(slow_patterns):
    for class_name in sorted(slow_patterns[plugin_name]):
        if len(slow_patterns[plugin_name][class_name]):
            plugin_slow_patterns = slow_patterns[plugin_name][class_name]
            for pattern in sorted(plugin_slow_patterns):
                us = slow_patterns[plugin_name][class_name][pattern]
                print("{:<20} {:<25} {:<35} {:>10}".format(plugin_name, class_name, pattern, us))

