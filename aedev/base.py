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

* :data:`COMMIT_MSG_FILE_NAME`: the default filename for commit messages.
* :data:`DEF_MAIN_BRANCH`: the name of the default/main branch.
* :data:`DEF_PROJECT_PARENT_FOLDER`: default directory name for grouping source code projects ('src').

* :data:`PIP_CMD`: the pip command - as used in a shell or on the command line.

* :data:`PYPI_PACKAGE_NAMES`: irregular project/package names, not convertable from their import names.
* :data:`PYPI_ROOT_URL`: the PyPI production host URL.
* :data:`PYPI_TEST_URL`: the PyPI test host URL.

* :data:`PROJECT_VERSION_SEP`: the separator used in Pip requirements files to ty/fix a project to a version.
* :data:`VERSION_QUOTE`: the quote character used for the `__version__` variable value (typically `'`).
* :data:`VERSION_PREFIX`: the search string used to find the `__version__` variable (e.g., `__version__ = '`).
* :data:`VERSION_MATCHER`: a pre-compiled regular expression to detect and manage version numbers conforming
  to :pep:`pep396 <396>` and python's `distutils` standards.

* :data:`DOCS_FOLDER`: default name for a project's documentation folder ('docs').
* :data:`TEMPLATES_FOLDER`: default name for a folder containing file templates ('templates').
* :data:`TESTS_FOLDER`: default name for a project's tests folder ('tests').

* :type:`TemplateProjectType`: project template register info (project_templates item type).
* :type:`TemplateProjectsType`: project_templates var type (added by pjm/project_manager).
* :type:`CachedTemplates`: cache mapping of registered project templates.

* :func:`code_file_title`: determines the docstring title of a Python code file.
* :func:`code_file_version`: reads the version number of a Python code file from the `__version__` module variable.
* :func:`code_version`: determines a version number from a specified content string (e.g., file content) using a
  configurable prefix and suffix.
* :func:`get_pypi_versions`: determines all available release versions of a package on PyPI.
* :func:`main_file_paths_parts`: returns a tuple of possible main/version file path names combinations of any project.
* :func:`project_main_file`: determines the absolute path to the main module file of a project package (where the
  `__version__` of the app|package is defined).
* :func:`project_name_version`: determine package name and version in the specified list of package/version strings.
* :func:`stripped_pip_name`: convert required project/distribution/package line into a normalized PyPI/pip package name.

an instance of the class :class:`PyMo` is representing a Python module/package, and provides:

* project, namespace, module, package and portion names
* project, module, package and portion paths
* dynamic load of a code module or package
"""
import importlib
import itertools
import json
import re
import sys

from collections.abc import Iterable
from types import ModuleType
from typing import Self
from urllib import request, error

from packaging.version import Version

from ae.base import (                                               # type: ignore
    env_str, norm_name, norm_path, os_path_basename, os_path_dirname, os_path_isfile, os_path_join, read_file)
from ae.app_log import ErrorMsgMixin                                # type: ignore
from ae.system import module_load, norm_pip_name, os_platform       # type: ignore


__version__ = '0.3.15'


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


COMMIT_MSG_FILE_NAME = '.commit_msg.txt'                #: default name of the file containing the commit message
DEF_MAIN_BRANCH = 'develop'                             #: default main/develop branch name
DEF_PROJECT_PARENT_FOLDER = 'src'                       #: default dir name to put code project roots underneath of it

NAME_PARTS_SPLITTER = re.compile("[" + "".join(('.', '_', '-')) + "]+")  #: PyPI/pip project names comparison :pep:`503`

PIP_CMD = "pip" if os_platform == 'win32' else "pip3"   #: pip command using python venvs, different especially on MSWin

PYPI_PACKAGE_NAMES = {
    'absl': 'absl-py',
    'airflow': 'apache-airflow',
    'allauth': 'django-allauth',
    'apt': 'python-apt',
    'arango': 'python-arango',
    'attr': 'attrs',
    'Bio': 'biopython',
    'bootstrap5': 'django-bootstrap5',
    'bs4': 'beautifulsoup4',
    'bson': 'pymongo',                                  # pymongo extension
    'cassandra': 'cassandra-driver',
    'cms': 'django-cms',
    'consul': 'python-consul',
    'corsheaders': 'django-cors-headers',
    'crispy_forms': 'django-crispy-forms',
    'crontab': 'python-crontab',
    'Crypto': 'pycryptodome',
    'cups': 'pycups',
    'cv2': 'opencv-python',
    'dateutil': 'python-dateutil',
    'dbus': 'dbus-python',
    'discord': 'discord.py',
    'dns': 'dnspython',
    'docx': 'python-docx',
    'dotenv': 'python-dotenv',
    'engineio': 'python-engineio',
    'faiss': 'faiss-cpu',                               # alternativ faiss-gpu
    'ffmpeg': 'ffmpeg-python',
    'filer': 'django-filer',
    'fitz': 'PyMuPDF',
    'fpdf': 'fpdf2',
    'gi': 'PyGObject',
    'git': 'GitPython',
    'github': 'PyGithub',
    'gitlab': 'python-gitlab',
    'gnupg': 'python-gnupg',
    'googleapiclient': 'google-api-python-client',
    'google.oauth2': 'google-auth',
    'google.protobuf': 'protobuf',
    'gridfs': 'pymongo',                                # pymongo extension
    'gtk': 'PyGTK',
    'haystack': 'django-haystack',
    'igraph': 'python-igraph',
    'jnius': 'pyjnius',
    'jose': 'python-jose',
    'jwt': 'PyJWT',
    'kafka': 'kafka-python',
    'ldap': 'python-ldap',
    'Levenshtein': 'python-Levenshtein',
    'magic': 'python-magic',
    'memcache': 'python-memcached',
    'menus': 'django-cms',                              # django-cms extension
    'multipart': 'python-multipart',
    'mysql': 'mysql-connector-python',
    'MySQLdb': 'mysqlclient',
    'nacl': 'PyNaCl',
    'nmap': 'python-nmap',
    'odf': 'odfpy',
    'OpenGL': 'PyOpenGL',
    'opensearchpy': 'opensearch-py',
    'OpenSSL': 'pyOpenSSL',
    'paho': 'paho-mqtt',
    'parler': 'django-parler',
    'PIL': 'pillow',
    'playhouse': 'peewee',                              # peewee extension
    'pptx': 'python-pptx',
    'psycopg2': 'psycopg2-binary',
    'pywt': 'PyWavelets',
    'rest_framework': 'djangorestframework',
    'RPi': 'RPi.GPIO',
    'rtmidi': 'python-rtmidi',
    'ruamel': 'ruamel.yaml',
    'sekizai': 'django-sekizai',
    'serial': 'pyserial',
    'skimage': 'scikit-image',
    'sklearn': 'scikit-learn',
    'slugify': 'python-slugify',
    'smbus': 'smbus2',
    'snappy': 'python-snappy',
    'socketio': 'python-socketio',
    'speech_recognition': 'SpeechRecognition',
    'storages': 'django-storages',
    'telegram': 'python-telegram-bot',
    'treebeard': 'django-treebeard',
    'usb': 'pyusb',
    'usb1': 'libusb1',
    'vlc': 'python-vlc',
    'websocket': 'websocket-client',
    'whois': 'python-whois',
    'win32api': 'pywin32',
    'win32com': 'pywin32',
    'wx': 'wxPython',
    'xlib': 'python-xlib',
    'yaml': 'PyYAML',
    'zmq': 'pyzmq',
}
""" irregular project/package names; not convertable directly/only from their import names. """


PROJECT_VERSION_SEP = '=='                              #: separates package name and version in pip req files

PYPI_ROOT_URL = "https://pypi.org"                      #: PyPI cheese shop production domain with service
PYPI_TEST_URL = "https://test.pypi.org"                 #: PyPI cheese shop test domain with service

DOCS_FOLDER = 'docs'                                    #: project root documentation default subfolder name
TEMPLATES_FOLDER = 'templates'                          #: templates default/standard subfolder name
TESTS_FOLDER = 'tests'                                  #: project root unit tests default subfolder name

TEST_PROJECTS_PARENT_FOLDER = 'TsT'                     #: integration/unit tests projects local machine parent folder
TEST_PROJECTS_NAMESPACE = 'aetst'                       #: integration/unit tests namespace
TEST_PROJECTS_REMOTE = 'gitlab.com'                     #: git remote domain of integration/unit tests projects

VERSION_QUOTE = "'"                                     #: quote character of the __version__ number variable value
VERSION_PREFIX = '__version__' + " = " + VERSION_QUOTE  #: search string to find the __version__ variable
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
    :param prefix:              version string prefix (directly before the version number).
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
    """ determine all the available release versions of a package hosted at the PyPI Cheese Shop.

    :param pip_name:            pip|package|project name to get release versions from.
    :param pypi_test:           pass `True` to use the test version of PyPI (at <test.pypi.org>). also if this argument
                                got not specified or is `None`, and the :paramref:`.pip_name` argument
                                starts with the test projects namespace (:data:`~aedev.base.TEST_PROJECTS_NAMESPACE`),
                                then the test version of PyPI will be used (e.g. for the pjm integration tests).
    :return:                    list of released versions (the latest one last) or
                                on error a list with a single empty string item.

    .. note:: if the OS environment variable `PIP_INDEX_URL` is set, then its value is used instead of `pypi.org`.

    """
    if pypi_test is None:
        pypi_test = pip_name.startswith(TEST_PROJECTS_NAMESPACE)    # no path to check for TEST_PROJECTS_PARENT_FOLDER
    pypi_root_url = PYPI_TEST_URL if pypi_test else (env_str("PIP_INDEX_URL") or "").rstrip("/") or PYPI_ROOT_URL

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


def main_file_paths_parts(portion_name: str) -> tuple[tuple[str, ...], ...]:
    """ determine possible/supported main/version file name and path parts, relative to the project root folder.

    :param portion_name:        portion or package name.
    :return:                    tuple of tuples of main/version file name path parts.
    """
    base_layouts = (
        ('__init__' + '.py', ),                                                 # flat layouts
        ('__main__' + '.py', ),
        ('main' + '.py', ),
        ('main', '__init__' + '.py'),
        (portion_name + '.py', ),
        (portion_name, '__init__' + '.py'),                                     # top-level layouts (e.g. Django)
        (portion_name, '__main__' + '.py'),
    )
    return base_layouts + tuple(("src", ) + layout for layout in base_layouts)  # base layouts + src layouts


def project_main_file(import_name: str, project_path: str = "") -> str:
    """ determine the main module file path of a project package containing the project __version__ module variable.

    :param import_name:         name of the module/package (including namespace prefixes, separated with dots).
    :param project_path:        optional path where the project of the package/module is situated. not needed if the
                                current working directory is the root folder of either the import_name project or of a
                                sister project (under the same project parent folder).
    :return:                    absolute file path of the main module or empty string if no main/version file is found.
    """
    *namespace_dirs, portion_name = PyMo(import_name).name_parts
    project_name = ('_'.join(namespace_dirs) + '_' if namespace_dirs else "") + portion_name
    paths_parts = main_file_paths_parts(portion_name)

    project_path = norm_path(project_path)
    module_paths = []
    if os_path_basename(project_path) != project_name:
        module_paths.append(os_path_join(os_path_dirname(project_path), project_name, *namespace_dirs))
    if namespace_dirs:
        module_paths.append(os_path_join(project_path, *namespace_dirs))
    module_paths.append(project_path)

    for module_path in module_paths:
        for path_parts in paths_parts:
            main_file = os_path_join(module_path, *path_parts)
            if os_path_isfile(main_file):
                return main_file
    return ""


def project_name_version(imp_or_pkg_name: str, packages_versions: Iterable[str]) -> tuple[str, str]:
    """ determine package name and version in the specified list of package/version strings.

    :param imp_or_pkg_name:     import or package name to search.
    :param packages_versions:   iterable where each item specifies a project via its project package name and an
                                optional version strings, like specified in requirements.txt files
                                (format: <project_name>[<:data:`PROJECT_VERSION_SEP`><project_version>]).
    :return:                    tuple of package name and version number. the package name is an empty string if it
                                is not in :paramref:`.packages_versions`. the version number is an
                                empty string if no package version is specified in
                                :paramref:`.packages_versions`.
    """
    project_name = norm_name(imp_or_pkg_name)
    for imp_or_pkg_name_and_ver in packages_versions:
        imp_or_pkg_name, *ver = imp_or_pkg_name_and_ver.split(PROJECT_VERSION_SEP)
        prj_name = norm_name(imp_or_pkg_name)
        if prj_name == project_name:
            return project_name, ver[0] if ver else ""
    return "", ""


def stripped_pip_name(req_project_name: str) -> str:
    """ convert a requiring project/distribution/package line from a requirements.txt file into a normalized pip name.

    :param req_project_name:    required project/distribution/package line with an optional version string or spaces.
    :return:                    stripped and normalized pip name of the specified PyPI project/distribution/package.
    """
    return norm_pip_name(req_project_name.strip().split(" ")[0].split(PROJECT_VERSION_SEP)[0])


class PyMo(ErrorMsgMixin):
    """ helper class to create, represent, inspect, load or import a Python module or package. """
    def __init__(self, import_name: str, project_path: str = "", **pypi_names: str) -> None:
        """ create a new instance of the class :class:`PyMo`.

        :param import_name:     import name of the module/package/portion.
        :param project_path:    optional project root folder path.
        :param pypi_names:      irregular PyPI project/distribution names; not convertable from their import names
                                (key_word==import name; value==PyPi distribution/project name). if the import name
                                contains a dot-character then specify this value as ``**dict``.
        """
        super().__init__()
        if not import_name:
            self.error_message = "Erroneous PyMo instance created with empty import name"

        self.import_name = import_name or 'import.name.error'
        self._project_path = project_path
        self._pypi_names = PYPI_PACKAGE_NAMES.copy()
        self._pypi_names.update(**pypi_names)

    @classmethod
    def from_name(cls, name: str, namespace_name: str = "", project_path: str = "", **pypi_names: str) -> Self:
        """ create a :class:`PyMo` instance from the name of a project/package/portion/module.

        :param name:            import/pip/package/project name of the module/package/portion.
        :param namespace_name:  namespace name/path w/ or w/o the module/portion name (at the end).
        :param project_path:    root folder path of the source project.
        :param pypi_names:      irregular PyPI project/distribution names; not convertable from their import names
                                (key_word==import name; value==PyPi distribution/project name).
        :return:                PyMo instance of the Python module/package/portion. specifying invalid arguments results
                                in an instance with an :attr:`~PyMo.import_name+` of 'import.name.error'.
        """
        name = (name or 'import.name.error').replace('-', '_')

        if namespace_name:
            import_name = ""
            for namespace_part in namespace_name.split('.'):
                if not name.startswith((namespace_part + '.', namespace_part + '_')):
                    break
                name = name[len(namespace_part) + 1:]
                import_name += namespace_part + '.'
            import_name += name
        else:
            import_name = name

        return cls(import_name, project_path=project_path, **pypi_names)

    @classmethod
    def from_path(cls, project_path: str, namespace_name: str = "", **pypi_names: str) -> Self:
        """ create a :class:`PyMo` instance from the specified project-root folder (source-code) path.

        :param project_path:    root folder path of the project source code.
        :param namespace_name:  namespace name/path with or without the module/portion name.
        :param pypi_names:      irregular PyPI project/distribution names; not convertable from their import names
                                (key_word==import name; value==PyPi distribution/project name).
        :return:                PyMo instance of the Python module/package/portion.
        """
        project_path = norm_path(project_path)
        project_name = os_path_basename(project_path)
        if namespace_name:
            return cls.from_name(project_name, namespace_name=namespace_name, project_path=project_path)

        import_name = project_name
        name_parts = NAME_PARTS_SPLITTER.split(project_name)
        joints = len(name_parts) - 1
        if joints >= 1:
            combinations = itertools.product(("/", ) + ('.', '_', '-'), repeat=joints)
            for combo in combinations:
                name = "".join(name_parts[i] + combo[i] for i in range(joints)) + name_parts[-1]
                *namespace_parts, portion_name = name.rsplit("/", maxsplit=1)
                for path_parts in main_file_paths_parts(portion_name):
                    if os_path_isfile(os_path_join(project_path, *namespace_parts, *path_parts)):
                        import_name = name.replace("/", '.')
                        break

        return cls(import_name.replace('-', '_'), project_path=project_path, **pypi_names)

    def __repr__(self):
        return f"PyMo('{self.import_name}', project_path='{self._project_path}', pypi_names={self._pypi_names})"

    def _warn(self, msg: str):
        self.error_message = f"{self.__class__.__name__}({self.import_name}) {msg}"

    @property
    def imported_module(self) -> ModuleType | None:
        """ try to import module, add it to sys.modules and return the spec of it (or `None` if not found/imported). """
        if self.import_name in sys.modules:
            return sys.modules[self.import_name]

        try:
            return importlib.import_module(self.import_name)
        except (ImportError, ModuleNotFoundError, Exception) as exc:  # pylint: disable=broad-exception-caught
            self._warn(f"imported_module raised {exc=}")

        return None

    @property
    def loaded_module(self) -> ModuleType | None:
        """ try to load module (without adding it to sys.modules). return the spec of it or `None` if not found. """
        mod_ref = module_load(self.import_name)
        if not isinstance(mod_ref, ModuleType):
            if self._project_path:
                mod_ref = module_load(self.import_name, path=self.package_file_path)
                if not isinstance(mod_ref, ModuleType):
                    mod_ref = module_load(self.import_name, path=self.module_file_path)

            if not isinstance(mod_ref, ModuleType):
                self.error_message = "\n".join(mod_ref)
                return None
        return mod_ref

    @property
    def module_file_path(self) -> str:
        """ module file path (absolute if project_path got specified, else relative to the project root folder). """
        return os_path_join(self._project_path, *self.name_parts) + '.py'

    @property
    def namespace_name(self) -> str:
        """ namespace name/path of the Python module/package represented by this instance. """
        return '.'.join(self.name_parts[:-1])

    @property
    def name_parts(self) -> list[str]:
        """ module-/portion-name parts of the Python module, including namespace name prefix(es). """
        return self.import_name.split('.')

    @property
    def package_name(self) -> str:
        """ name of the package/project of the Python module. """
        return '_'.join(self.name_parts)

    @property
    def package_file_path(self) -> str:
        """ package path w/ '__init__' + '.py' (and project_path if specified, else relative to the project root). """
        return os_path_join(self._project_path, *self.name_parts, '__init__' + '.py')

    @property
    def pip_name(self) -> str:
        """ pip&PyPI package name of the Python module. """
        return norm_pip_name(self.project_name)

    @property
    def portion_name(self) -> str:
        """ name of the Python module """
        return self.name_parts[-1]

    @property
    def project_name(self) -> str:
        """ name of the Python distribution/project (could differ from the :attr:`~PyMo.package_name` property). """
        return self._pypi_names.get(self.import_name, self.package_name)

    @property
    def project_root_path(self) -> str:
        """ normalized absolute project root path of the Python module. """
        return norm_path(self._project_path or self.package_name)
