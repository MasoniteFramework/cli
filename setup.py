from setuptools import setup

setup(
    name="masonite-cli",
    version='0.30.1',
    py_modules=['craft'],
    packages=['snippets', 'snippets.auth', 'snippets.auth.controllers', 'snippets.auth.templates.auth'],
    install_requires=[
        'Click',
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        craft=craft:group
        craft-vendor=craft:cli
    ''',
)
