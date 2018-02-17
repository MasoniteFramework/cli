from setuptools import setup

setup(
    name="masonite-cli",
    version='1.0.2',
    py_modules=['craft'],
    packages=[
        'masonite_snippets'
    ],
    install_requires=[
        'Click',
        'cryptography==2.1.4',
        'requests==2.18.4',
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        craft=craft:group
        craft-vendor=craft:cli
    ''',
)
