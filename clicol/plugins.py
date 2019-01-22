from __future__ import print_function
from __future__ import unicode_literals

import re
from pkg_resources import iter_entry_points

import pudb

class Plugins:

    'Registered plugins'
    registered = list()
    'To process plugins'
    active = list()
    debug = False

    def __init__(self, debug = False):
        #pudb.set_trace()
        self.debug = debug
        for entrypoint in iter_entry_points('clicol.plugins'):
            plugin = entrypoint.load()
            'Register builtin plugins'
            self.register(plugin())
        return


    'Run active plugins'
    def preprocess(self, input):
        #pudb.set_trace()
        for plugin in self.active:
            try:
                input = plugin.preprocess(input)
            except AttributeError:
                pass
        return input

    'Run active plugins'
    def postprocess(self, input):
        #pudb.set_trace()
        for plugin in self.active:
            try:
                input = plugin.postprocess(input)
            except AttributeError:
                pass
        return input

    def register(self, plugin):
        try:
            self.registered.append(plugin)
            if self.debug: print("Plugin %s registered" % plugin)
            if plugin.loadonstart:
                self.active.append(plugin)
        except:
            pass
