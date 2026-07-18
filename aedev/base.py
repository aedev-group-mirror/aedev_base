"""
base development constants and helpers
======================================

this module portion in the aedev namespace provides the following base constants, types and helper functions, used for
development operations (DevOps) and tools:

* :data:`APP_PRJ` – gui application project type.
* :data:`DJANGO_PRJ` – django web application project type.
* :data:`MODULE_PRJ` – standalone module project type.
* :data:`NO_PRJ` – marker for invalid or no project (type) detected.
* :data:`PACKAGE_PRJ` – python package project type.
* :data:`PARENT_PRJ` – pseudo-type for parent-directory initialization.
* :data:`PLAYGROUND_PRJ` – playground or scratch project type.
* :data:`ROOT_PRJ` – namespace root project type.
* :data:`ANY_PRJ_TYPE` – tuple of all real project types.
* :data:`ALL_PRJ_TYPES` – tuple of all project types, including :data:`NO_PRJ` and :data:`PARENT_PRJ`.

- :data:`COMMIT_MSG_FILE_NAME`: the default filename for commit messages.
- :data:`DEF_MAIN_BRANCH`: the name of the default/main branch.

- :data:`PIP_CMD`: the pip command - as used in a shell or on the command line.

- :data:`PYPI_ROOT_URL`: the production PyPI URL.
- :data:`PYPI_ROOT_URL_TEST`: the test PyPI URL.

- :data:`PROJECT_VERSION_SEP`: the separator used in Pip requirements files to ty/fix a project to a version.
- :data:`VERSION_QUOTE`: the quote character used for the `__version__` variable value (typically `'`).
- :data:`VERSION_PREFIX`: the search string used to find the `__version__` variable (e.g., `__version__ = '`).
- :data:`VERSION_MATCHER`: a pre-compiled regular expression to detect and manage version numbers conforming
  to :pep:`pep396 <396>` and python's `distutils` standards.

- :type:`TemplateProjectType`: project template register info (project_templates item type).
- :type:`TemplateProjectsType`: project_templates var type (added by pjm/project_manager).
- :type:`CachedTemplates`: cache mapping of registered project templates.

- :func:`code_file_title`: determines the docstring title of a Python code file.
- :func:`code_file_version`: reads the version number of a Python code file from the `__version__` module variable.
- :func:`code_version`: determines a version number from a specified content string (e.g., file content) using a
  configurable prefix and suffix.
- :func:`get_pypi_versions`: determines all available release versions of a package on PyPI.
- :func:`project_name_version`: determine package name and version in the specified list of package/version strings.

"""
import json
import re

from collections.abc import Iterable
from urllib import request, error

from packaging.version import Version

from ae.base import env_str, norm_name, read_file       # type: ignore
from ae.system import os_platform                       # type: ignore


__version__ = '0.3.9'


APP_PRJ = 'app'                                         #: gui application project
DJANGO_PRJ = 'django'                                   #: django website project
MODULE_PRJ = 'module'                                   #: module portion/project
NO_PRJ = ''                                             #: no project detected
PACKAGE_PRJ = 'package'                                 #: package portion/project
PARENT_PRJ = 'projects-parent-dir'                      #: pseudo project type for new project started in parent-dir
PLAYGROUND_PRJ = 'playground'                           #: playground project
ROOT_PRJ = 'namespace-root'                             #: namespace root project

ANY_PRJ_TYPE = (APP_PRJ, DJANGO_PRJ, MODULE_PRJ, PACKAGE_PRJ, PLAYGROUND_PRJ, ROOT_PRJ)
""" tuple of real project types (not including the pseudo-project-types: no-/incomplete-project and parent-folder) """
ALL_PRJ_TYPES = ANY_PRJ_TYPE + (NO_PRJ, PARENT_PRJ)     #: all project types (including no/parent project)


COMMIT_MSG_FILE_NAME = '.commit_msg.txt'                #: name of the file containing the commit message
DEF_MAIN_BRANCH = 'develop'                             #: main/develop/default branch name

PIP_CMD = "pip" if os_platform == 'win32' else "pip3"   #: pip command using python venvs, different especially on MSWin

PROJECT_VERSION_SEP = '=='                              #: separates package name and version in pip req files

PYPI_ROOT_URL = "https://pypi.org"                      #: PyPI cheeseshop production domain with service
PYPI_ROOT_URL_TEST = "https://test.pypi.org"            #: PyPI cheeseshop test domain with service

TEST_PROJECTS_PARENT_FOLDER = 'TsT'                     #: integration/unit tests projects local machine parent folder
TEST_PROJECTS_NAMESPACE = 'aetst'                       #: integration/unit tests namespace
TEST_PROJECTS_REMOTE = 'gitlab.com'                     #: git remote domain of integration/unit tests projects

VERSION_QUOTE = "'"                                     #: quote character of the __version__ number variable value
VERSION_PREFIX = "__version__ = " + VERSION_QUOTE       #: search string to find the __version__ variable
VERSION_MATCHER = re.compile("^" + VERSION_PREFIX + r"(\d+)[.](\d+)[.](\d+)[a-z\d]*" + VERSION_QUOTE, re.MULTILINE)
""" pre-compiled regular expression to detect and change/bump the app/portion file version numbers of a version string.

The version number format has to be :pep:`conform to PEP396 <396>` and the sub-part to `Pythons distutils
<https://docs.python.org/3/distutils/setupscript.html#additional-meta-data>`__ (trailing version information indicating
sub-releases, are either “a1,a2,…,aN” (for alpha releases), “b1,b2,…,bN” (for beta releases) or “pr1,pr2,…,prN” (for
pre-releases). Note that distutils got deprecated in Python 3.12 (see package :mod:`packaging.version` as replacement)).
"""


TemplateProjectType = dict[str, str]                    #: project template register info (project_templates item type)
TemplateProjectsType = list[TemplateProjectType]        #: project_templates var type (added by pjm/project_manager)
CachedTemplates = dict[str, TemplateProjectType]        #: cache mapping of registered project templates


def code_file_title(file_name: str) -> str:
    """ determine docstring title of a Python code file.

    :param file_name:           name (and optional path) of module/script file to read the docstring title number from.
    :return:                    docstring title string or empty string if file|docstring-title not found.
    """
    title = ""
    try:
        lines = read_file(file_name).splitlines()
        for idx, line in enumerate(lines):
            if line.startswith('"""'):
                title = (line[3:].strip() or lines[idx + 1].strip()).strip('"').strip()
                break
    except (FileNotFoundError, IndexError, OSError):
        pass
    return title


def code_file_version(file_name: str) -> str:
    """ read version of Python code file - from __version__ module variable initialization.

    :param file_name:           name (and optional path) of module/script file to read the version number from.
    :return:                    version number string or empty string if file or version-in-file not found.
    """
    try:
        content = read_file(file_name)
        return code_version(content)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return ""


def code_version(content: str | bytes, prefix: str = "^" + VERSION_PREFIX, suffix: str = VERSION_QUOTE) -> str:
    """ determine a version number from the specified content string.

    :param content:             content of type str or bytes to be searched for the definition/declaration of a version.
    :param prefix:              version string prefix (directly before the veesion number).
    :param suffix:              version string suffix char/string (directly after the version number string).
                                passing an empty is not allowed, and will always return an empty string.
    :return:                    version number string or empty string if version could not be not found in content.
    """
    try:
        pattern = prefix + "([^" + suffix + "]*)" + suffix
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        version_match = re.search(pattern, content, re.M)
        return version_match.group(1) if version_match else ""
    except (TypeError, UnicodeDecodeError, ValueError, Exception):  # pylint: disable=broad-exception-caught
        return ""


def get_pypi_versions(pip_name: str, pypi_test: bool | None = None) -> list[str]:
    """ determine all the available release versions of a package hosted at the PyPI 'Cheese Shop'.

    :param pip_name:            pip|package|project name to get release versions from.
    :param pypi_test:           pass True to use the test version of PyPI (at test.pypi.org). if not specified or None
                                then the test version of PyPI will be used if :paramref:`~get_pypi_versions.pip_name`
                                starts with the projects namespace (:data:`~aedev.base.TEST_PROJECTS_NAMESPACE),
                                used for the pjm integration tests.
    :return:                    list of released versions (the latest last) or
                                on error a list with a single empty string item.
    .. note:: if the OS environment variable ``PIP_INDEX_URL`` is set, then its value is used instead of ``pypi.org``.
    """
    if pypi_test is None:
        pypi_test = pip_name.startswith(TEST_PROJECTS_NAMESPACE)    # no path to check for TEST_PROJECTS_PARENT_FOLDER
    pypi_root_url = PYPI_ROOT_URL_TEST if pypi_test else (env_str("PIP_INDEX_URL") or "").rstrip("/") or PYPI_ROOT_URL

    try:
        with request.urlopen(f"{pypi_root_url}/pypi/{pip_name}/json", timeout=12) as response:
            if response.status == 200:
                data = json.load(response)  # faster than: json.loads(response.read().decode('utf-8'))
                versions = list(data.get('releases', {}).keys())
                if versions:
                    versions.sort(key=Version)
                    return versions

    except (KeyError, ValueError, error.HTTPError, error.URLError, Exception):  # pylint: disable=broad-exception-caught
        pass                                                        # Exception is catching also json.JSONDecodeError

    return [""]         # ignore error on invalid pip_name/page-not-found/never released to PyPi


def project_name_version(imp_or_pkg_name: str, packages_versions: Iterable[str]) -> tuple[str, str]:
    """ determine package name and version in the specified list of package/version strings.

    :param imp_or_pkg_name:     import or package name to search.
    :param packages_versions:   an Iterable with project package name and optional version strings, like specified in
                                requirements.txt files (format: <project_name>[<PROJECT_VERSION_SEP><project_version>]).
    :return:                    tuple of package name and version number. the package name is an empty string if it
                                is not in :paramref:`~project_version.packages_versions`. the version number is an
                                empty string if no package version is specified in
                                :paramref:`~project_version.packages_versions`.
    """
    project_name = norm_name(imp_or_pkg_name)
    for imp_or_pkg_name_and_ver in packages_versions:
        imp_or_pkg_name, *ver = imp_or_pkg_name_and_ver.split(PROJECT_VERSION_SEP)
        prj_name = norm_name(imp_or_pkg_name)
        if prj_name == project_name:
            return project_name, ver[0] if ver else ""
    return "", ""
