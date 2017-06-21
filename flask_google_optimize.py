# -*- coding: utf-8 -*-

__version__ = '0.0.1.dev0'


class GoogleOptimize(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass
