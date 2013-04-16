from setuptools import setup

PACKAGE = 'ChangesetValidator'
VERSION = '0.1'

setup(
    name=PACKAGE,
    version=VERSION,
    description='Changeset validation routines',
    author="SDAttractor",
    author_email="info@sdattractor.com",
    license='',
    url='',
    packages=['changesetvalidator'],
    entry_points={
        'trac.plugins': [
            'changesetvalidator.command = changesetvalidator.command',
        ]
    },
    package_data={
        'changesetvalidator': [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'templates/*.html',
        ],
    }
)
