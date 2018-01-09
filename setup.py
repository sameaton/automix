from setuptools import setup

setup(
    name='automix',
    version='0.1',
    py_modules=['automix'],
    install_requires=[
        'Click',
        'numpy',
        'scipy',
        'soundfile'
    ],
    entry_points='''
        [console_scripts]
        automix=automix:automix
    ''',
)
