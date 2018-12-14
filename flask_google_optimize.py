# -*- coding: utf-8 -*-

from flask import request
from jinja2 import Markup
import random


__version__ = '0.1.3'


class GoogleOptimize(object):

    def __init__(self, app=None):
        self.app = app
        self._experiments = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        @app.before_request
        def before_request_handler():
            request.optimize = Context(self)

        @app.after_request
        def after_request_handler(response):
            request.optimize.set_cookies(response)
            return response

    def declare_experiment(self, key, id, variations):
        """
        Declare a new A/B test

        :param key: String. A human readable name of the variation. This should be a valid python identifier
        :param id: String.The associated Optimize ID of the experiment.
        :param variations: A List used to declare the different variations and their respective distribution:
        [{'key': 'small', 'weight': 0.5}, {'key': 'big', 'weight': 0.5}]
        """
        self._experiments[key] = Experiment(
            key=key,
            id=id,
            variations=variations
        )

    def get_exp(self, key=None, id=None):
        if key:
            return self._experiments[key]
        if id:
            return [e for e in self._experiments if e.id == id][0]

    def get_all_experiments(self):
        return self._experiments.values()


class Experiment(object):

    def __init__(self, key, id, variations):
        self.key = key
        self.id = id
        self.variations = variations  # [{'key': 'small', 'weight': 0.5},...]
        self._validate_variations()

    def _validate_variations(self):
        """
        Validate that all the weight for each variation is a valid float number and the sum of all weight is <= 1

        :raises TypeError or ValueError: is the validation fails
        """

        weights = [float(variation['weight']) for variation in self.variations]
        if sum(weights) > 1.0:
            raise ValueError('The sum of all your weights should not exceed 1.0')

    def get_var_id(self, key):
        return [variation_index
                for (variation_index, variation) in enumerate(self.variations) if variation['key'] == key][0]

    def get_var_key(self, id):
        return self.variations[id]['key']


class Context(object):
    """
    Choice of variations for each relevant experiment in the context of a request.
    """

    def __init__(self, optimize):
        self.optimize = optimize
        self._active_variations = {}  # {exp_key: var_id}

    def run(self, experiment_key):
        """
        Enable an experiment in the current request and choose the most appropriate variation: either the one to which
        the user is already assigned to (if it's still declared), or randomly pick one.
        """
        experiment = self.optimize.get_exp(experiment_key)

        # Try to get the current variation for this user from the cookie
        try:
            cookie_value = int(self.get_cookie_value(experiment.id))
        except (TypeError, ValueError, UnicodeDecodeError):
            # TypeError to handle None value
            # ValueError to handle strings with non integer values
            # UnicodeDecodeError for strings with non western characters, like Chinese...
            cookie_value = None

        # Reuse the cookie if it points to a valid variation, otherwise assign a random variation
        try:
            cookie_value = int(cookie_value)
            if not (0 <= cookie_value < len(experiment.variations)):
                # Cookie value ia a garbage number, just ignore it and rerun the experiment for this user
                raise ValueError
            variation_id = cookie_value
        except (TypeError, ValueError):
            variation_id = self._choose_variation(experiment.variations)

        self._active_variations[experiment.key] = variation_id

    def _choose_variation(self, variations):
        """
        Return the index of the randomly chosen variation. Choice is by default non uniform and depends on the weight
        of each variation (you can of course simulate a uniform variation by giving the same weight to each variation)

        Implementation algorithm is quite simple : we construct a list of variation indexes. Each index is repeated
        more or less depending on its weight. And then it's just a matter of using the random.choice function
        to randomly pick a choice in this weighted list.

        :param variations: A list of {'key':..., 'weight'...}
        :return: Integer. The index of the chosen variation from variations
        """
        weighted_variation_list = []
        for index, variation in enumerate(variations):
            variation_list = [index for _ in range(0, int(variation['weight'] * 100))]
            weighted_variation_list.extend(variation_list)

        return random.choice(weighted_variation_list)

    def wake_up(self):
        """
        Retrieve the assigned variations for the declared experiments that have been run earlier.
        """

        for exp in self.optimize.get_all_experiments():
            cookie_value = self.get_cookie_value(exp.id)
            if cookie_value and int(cookie_value) in exp.variations:
                self._active_variations[exp.key] = int(cookie_value)

    def get_cookie_value(self, exp_id):
        """
        Get the value of the cookie corresponding to the given experiment ID, regardless of whether the experiment ID
        corresponds to a declared experiment.
        """
        return request.cookies.get('flask_google_optimize__{}'.format(exp_id))

    def set_cookies(self, response):
        """
        Set the appropriate cookies on `response` so that the assigned variations to the enabled experiments are saved
        until the next hit.
        """
        for exp_key, var_id in self._active_variations.iteritems():
            experiment = self.optimize.get_exp(exp_key)
            response.set_cookie(
                key='flask_google_optimize__{}'.format(experiment.id),
                value=str(var_id),
                max_age=3600 * 24 * 30
            )

    def __getattr__(self, experiment_key):
        """
        Shorthand to `self.variations['<experiment_key>']`.
        """
        return self.variations[experiment_key]['key']

    @property
    def js_snippet(self):
        """
        JavaScript code to insert into the Google Analytics snippet in order to tell Google Optimize which variation
        was chosen on each enabled test.
        """

        code = ''

        for exp_key, var_id in self._active_variations.iteritems():
            exp = self.optimize.get_exp(exp_key)
            code += "ga('set', 'exp', '{}.{}');\n".format(exp.id, var_id)

        return Markup(code)

    @property
    def variations(self):
        return {
            exp_key: self.optimize.get_exp(key=exp_key).variations[var_id]
            for exp_key, var_id in self._active_variations.iteritems()
        }
