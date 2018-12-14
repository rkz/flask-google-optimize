# Flask-Google-Optimize

## Purpose

(Coming soon)

## Tutorial

### Setup

Setup your app and hook the extension:

```python
from flask_google_optimize import GoogleOptimize
app = Flask()
optimize = GoogleOptimize(app)
```

Describe all the experiments currently running in Google Optimize. Give them meaningful identifiers for the Python code. Let's say you have an experiment on the size of your CTAs with three variations:

```python
optimize.declare_experiment(
    key='cta_size',
    id='16iQisXuS1qwXDixwB-EWgQ',
    variations=[
        {'key': None, 'weight': 0.33},
        {'key': 'bigger', 'weight': 0.33},
        {'key': 'smaller', 'weight': 0.33}
    ]
)
```

Do the same for every running experiment.

### View functions

In the view function where you'll need the template to know which variation the user is assigned to, use `run()`. 

```python
from flask import render_template, request

@app.route('/cart')
def cart():
    request.optimize.run('cta_size')
    return render_template('cart.html')
```

Flask-Google-Optimize takes care of assigning the user to the same variation using a cookie; on the first hit where an experiment is running, it assigns to a random variation.

### Template

The selected variation is then available in the template. Let's use it to make the size of our CTAs vary:

```jinja2
<div>
    {% if request.optimize.cta_size is None %}
        <button class="btn btn-default">Purchase</button>
    {% elif request.optimize.cta_size == 'bigger' %}
        <button class="btn btn-default btn-lg">Purchase</button>
    {% elif request.optimize.cta_size == 'smaller' %}
        <button class="btn btn-default btn-xs">Purchase</button>
    {% endif %}
</div>
```

You must also report the chosen variations to Google Optimize, through [specific calls in the Analytics snippet](https://developers.google.com/optimize/devguides/experiments#add-ga-tracking-code-to-variations):

```html
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-XXXXX-Y', 'auto');

  {{ request.optimize.js_snippet }}

  ga('send', 'pageview');
</script>
```

## See also

https://developers.google.com/optimize/devguides/experiments

## Roadmap

- Flask Debug Toolbar extension
- Better error reporting for edge cases
- Customize the cookie duration
