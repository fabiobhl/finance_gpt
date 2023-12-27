from setuptools import setup, find_packages

setup(
    name='finance_gpt',
    version='1.0',
    description='GPT sentiment analysis for finance',
    author='Fabio Buehler',
    author_email="fabiobuehler10@gmail.com",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)