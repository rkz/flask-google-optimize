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
        @app.before_request
        def before_request_handler():
            request.optimize = {}

        @app.after_request
        def after_request_handler(response):
            for exp_key, var_key in request.optimize.iteritems():
                experiment = self.get_exp(exp_key)
                response.set_cookie(
                    key='optimize_{}'.format(experiment.id),
                    value=str(experiment.get_var_id(var_key)),
                    max_age=3600 * 24 * 30
                )
            return response

    def declare_experiment(self, key, id, variations):
        self._experiments[key] = Experiment(
            key=key,
            id=id,
            variations=variations
        )

    def run(self, key):
        if key not in self._experiments:
            raise ValueError(u"No experiment with key '{}'".format(key))

        experiment = self.get_exp(key=key)

        if key in request.optimize:  # test has already been ran in the request
            return

        # Reuse the cookie if it points to a valid variation, otherwise assign a random variation
        cookie_key = 'optimize_{}'.format(experiment.id)
        cookie_value = request.cookies.get(cookie_key)
        if cookie_value and int(cookie_value) in experiment.variations:
            variation = int(cookie_value)
        else:
            variation = random.randint(0, len(experiment.variations) - 1)

        request.optimize[key] = experiment.get_var_key(variation)

    def get_exp(self, key=None, id=None):
        if key:
            return self._experiments[key]
        if id:
            return [e for e in self._experiments if e['id'] == id][0]


class Experiment(object):

    def __init__(self, key, id, variations):
        self.key = key
        self.id = id
        self.variations = variations

    def get_var_id(self, key):
        return [var_id for (var_id, var_key) in self.variations.iteritems() if var_key == key][0]

    def get_var_key(self, id):
        return self.variations[id]
