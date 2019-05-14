from __future__ import print_function
from __future__ import unicode_literals

import re
from pkg_resources import iter_entry_points

class Plugins:

    'Registered plugins'
    registered = list()
    'To process plugins'
    active = list()
    tests = list()
    debug = False

    def __init__(self, debug = False, setup=(dict(),dict())):
        self.debug = debug
        (pluginsetups, colormap) = setup
        for entrypoint in iter_entry_points('clicol.plugins'):
            plugin = entrypoint.load()
            pluginsetup = dict()
            'Plugins have to have a section in plugins.cfg'
            if pluginsetups.has_section(entrypoint.name.lower()):
                pluginsetup = dict(pluginsetups.items(entrypoint.name.lower()))
                if 'active' in pluginsetup.keys():
                    if not pluginsetup['active'] in ['1','True','true','yes','Yes','On','on']:
                        continue
                'Register plugins'
                self.register(plugin((pluginsetup, colormap)))
        return


    'Run active plugins'
    def preprocess(self, input, effects = []):
        for plugin in self.active:
            try:
                input = plugin.preprocess(input, effects)
            except AttributeError:
                pass
        return input

    'Run active plugins'
    def postprocess(self, input, effects = []):
        for plugin in self.active:
            try:
                input = plugin.postprocess(input, effects)
            except AttributeError:
                pass
        return input

    def register(self, plugin):
        try:
            self.registered.append(plugin)
            if self.debug: print("Plugin %s registered" % plugin)
            if plugin.loadonstart:
                self.active.append(plugin)
                try:
                    self.tests.append(plugin.test)
                except AttributeError:
                    pass
        except:
            pass

    def tests(self):
        input = ""
        for plugin in self.active:
            try:
                input += ": ".join(plugin.test())
                input += "\r\n"
            except AttributeError:
                pass
        return input
