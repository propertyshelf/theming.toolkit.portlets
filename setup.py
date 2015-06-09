# -*- coding: utf-8 -*-
"""Installer for the theming.toolkit.portlets package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='theming.toolkit.portlets',
    version='0.1',
    description="Adds a set of useful portlets to MLS embedding websites",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3.4",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Plone',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='http://pypi.python.org/pypi/theming.toolkit.portlets',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['theming', 'theming.toolkit'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'z3c.jbot',
        'ps.plone.mls',
        'plone.mls.listing',
        'mls.apiclient',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
