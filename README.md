# Flask-Google-Optimize

## Usage

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
    variations={
        0: None,
        1: 'bigger',
        2: 'smaller'
    }
)
```

Do the same for every running experiment.

### View functions

In the view function where you'll need the template to know which variation the user is assigned to, use `run()`. 

```python
@app.route('/cart')
def cart():
    optimize.run('cta_size')
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

## See also

https://developers.google.com/optimize/devguides/experiments
