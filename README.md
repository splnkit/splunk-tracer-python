# splunk-tracer-python

[![MIT license](http://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)

The Splunk distributed tracing library for Python.

## Installation

```bash
apt-get install python-dev
pip install splunk-tracer
```

## Developer Setup

### Prerequisites
* [PyEnv](https://github.com/pyenv/pyenv)

```python
pyenv install 2.7.15
pyenv install 3.4.9
pyenv install 3.5.6
pyenv install 3.6.6
pyenv install 3.7.0
pyenv local 2.7.15 3.4.9
```

* [Tox](https://pypi.org/project/tox/)
```python
tox
```

* Run the examples:
```python
source .tox/py37/bin/activate
python examples/nontrivial/main.py
```

* [Python-Modernize](https://github.com/python-modernize/python-modernize)

Only required for developers
```python
pip install modernize
```


## Getting Started with Tracing

Please see the [example programs](examples/) for examples of how to use this library. In particular:

* [Trivial Example](examples/trivial/main.py) shows how to use the library on a single host.
* [Context in Headers](examples/http/context_in_headers.py) shows how to pass a `TraceContext` through `HTTP` headers.

Or if your python code is already instrumented for OpenTracing, you can simply switch to Splunk's implementation with:

```python
import opentracing
import splunktracing

if __name__ == "__main__":
  opentracing.tracer = splunktracing.Tracer(
    component_name='your_microservice_name',
    access_token='{your_hec_token}')

  with opentracing.tracer.start_active_span('TestSpan') as scope:
    scope.span.log_event('test message', payload={'life': 42})

  opentracing.tracer.flush()
```


This library is the Splunk binding for [OpenTracing](http://opentracing.io/). See the [OpenTracing Python API](https://github.com/opentracing/opentracing-python) for additional detail.

## License

The Splunk Tracer for Python is licensed under the MIT License. Details can be found in the LICENSE file.

### Third-party libraries

This is a fork of the Python tracer from Lightstep, which is also licensed under the MIT License. Links to the original repository and license are below:

* [lightstep-tracer-python][lightstep]: [MIT][lightstep-license]

[lightstep]:                      https://github.com/lightstep/lightstep-tracer-python
[lightstep-license]:              https://github.com/lightstep/lightstep-tracer-python/blob/master/LICENSE

