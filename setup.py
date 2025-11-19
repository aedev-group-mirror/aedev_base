# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.68
""" setup of aedev namespace module portion base: base development constants and helpers. """
# noinspection PyUnresolvedReferences
import sys
print(f"SetUp {__name__=} {sys.executable=} {sys.argv=} {sys.path=}")

# noinspection PyUnresolvedReferences
import setuptools

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [       'Development Status :: 3 - Alpha', 'Natural Language :: English', 'Operating System :: OS Independent',
        'Programming Language :: Python', 'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12', 'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed'],
    'description': 'aedev namespace module portion base: base development constants and helpers',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'aedev_aedev', 'anybadge', 'coverage-badge', 'aedev_project_manager',
                       'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing',
                       'types-setuptools'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_project_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.aedev v0.3.28 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.21 -->\n'
 '# base 0.3.1\n'
 '\n'
 '[![GitLab develop](https://img.shields.io/gitlab/pipeline/aedev-group/aedev_base/develop?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_base)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/aedev-group/aedev_base/release0.3.1?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_base/-/tree/release0.3.1)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/aedev_base)](\n'
 '    https://pypi.org/project/aedev-base/#history)\n'
 '\n'
 '>aedev namespace module portion base: base development constants and helpers.\n'
 '\n'
 '[![Coverage](https://aedev-group.gitlab.io/aedev_base/coverage.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_base/coverage/index.html)\n'
 '[![MyPyPrecision](https://aedev-group.gitlab.io/aedev_base/mypy.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_base/lineprecision.txt)\n'
 '[![PyLintScore](https://aedev-group.gitlab.io/aedev_base/pylint.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_base/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/aedev_base)](\n'
 '    https://gitlab.com/aedev-group/aedev_base/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/aedev_base)](\n'
 '    https://gitlab.com/aedev-group/aedev_base/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/aedev_base)](\n'
 '    https://gitlab.com/aedev-group/aedev_base/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/aedev_base)](\n'
 '    https://pypi.org/project/aedev-base/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/aedev_base)](\n'
 '    https://gitlab.com/aedev-group/aedev_base/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/aedev_base)](\n'
 '    https://libraries.io/pypi/aedev-base)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/aedev_base)](\n'
 '    https://pypi.org/project/aedev-base/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'aedev.base module\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install aedev-base\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the aedev_base repository at GitLab](\n'
 'https://gitlab.com/aedev-group/aedev_base "aedev.base code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(aedev_base):\n'
 '\n'
 '```shell script\n'
 'pip install -e .[dev]\n'
 '```\n'
 '\n'
 'the last command will install this module portion, along with the tools you need\n'
 'to develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\n'
 'documentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\n'
 'respectively.\n'
 '\n'
 'more detailed explanations on how to contribute to this project\n'
 '[are available here](\n'
 'https://gitlab.com/aedev-group/aedev_base/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.base.html\n'
 '"aedev_base documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_base',
    'package_data': {'': []},
    'packages': ['aedev'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_base/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.base.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_base',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/base.html'},
    'python_requires': '>=3.12',
    'url': 'https://gitlab.com/aedev-group/aedev_base',
    'version': '0.3.1',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
