from setuptools import setup, find_packages

setup(
    name='splunk-tracer',
    version='0.1.0',
    description='Splunk Python OpenTracing Implementation',
    long_description='',
    author='SplunkDev',
    license='MIT',
    install_requires=['six',
                      'basictracer>=3.0,<4',
                      'requests>=2.19,<3.0'],
    tests_require=['pytest',
                   'sphinx',
                   'sphinx-epytext'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],

    keywords=[ 'opentracing', 'splunk', 'traceguide', 'tracing', 'microservices', 'distributed' ],
    packages=find_packages(exclude=['docs*', 'tests*', 'sample*']),
)
