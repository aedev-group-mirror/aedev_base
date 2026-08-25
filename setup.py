# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.102
""" setup of aedev namespace module portion base: base development constants and helpers. """
import pathlib
import sys
from typing import Any
import setuptools


print("SetUp " + __name__ + ": " + sys.executable + str(sys.argv) + f" {sys.path=}")

setup_kwargs: dict[str, Any] = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    'description': 'aedev namespace module portion base: base development constants and helpers',
    'extras_require': {
        'dev': [
            'aedev_project_tpls',
            'aedev_aedev',
            'anybadge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'typing',
            'types-setuptools',
        ],
        'docs': [],
        'tests': [
            'anybadge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'typing',
            'types-setuptools',
        ],
    },
    'install_requires': [
        'packaging',
        'ae_base',
        'ae_system',
    ],
    'keywords': [
        'configuration',
        'development',
        'environment',
        'productivity',
    ],
    'license': 'GPL-3.0-or-later',
    'long_description': (pathlib.Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_base',
    'package_data': {
        '': [],
    },
    'packages': [
        'aedev',
    ],
    'project_urls': {
        'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_base/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.base.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_base',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/base.html',
    },
    'python_requires': '>=3.12',
    'url': 'https://gitlab.com/aedev-group/aedev_base',
    'version': '0.3.11',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    ...
