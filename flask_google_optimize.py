# -*- coding: utf-8 -*-

from flask import request
import random


__version__ = '0.0.1.dev0'


class GoogleOptimize(object):

    def __init__(self, app=None):
        self.app = app
        self._experiments = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # TODO: attach an after_request handler to set cookie

    def declare_experiment(self, key, id, variations):
        self._experiments[key] = {
            'id': id,
            'variations': variations
        }

    def run(self, key):
        if key not in self._experiments:
            raise ValueError(u"No experiment with key '{}'".format(key))

        experiment = self._experiments[key]

        if not hasattr(request, 'optimize'):
            request.optimize = {}

        if key in request.optimize:  # test has already been ran in the request
            return

        # Reuse the cookie if it points to a valid variation, otherwise assign a random variation
        cookie_key = 'optimize_{}'.format(experiment['id'])
        cookie_value = request.cookies.get(cookie_key)
        if cookie_value and int(cookie_value) in experiment['variations']:
            variation = int(cookie_value)
        else:
            variation = random.randint(0, len(experiment['variations']))

        request.optimize[key] = variation
