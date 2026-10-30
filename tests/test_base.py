""" aedev.base unit tests """
import os
import re

from types import ModuleType

import pytest

from ae.base import (
    norm_path, os_path_basename, os_path_dirname, os_path_isdir, os_path_join, os_path_relpath, url_failure, write_file)
from ae.system import norm_pip_name

from tests.conftest import skip_gitlab_ci


from aedev.base import (
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, PLAYGROUND_PRJ, ROOT_PRJ,
    ANY_PRJ_TYPE, ALL_PRJ_TYPES,
    COMMIT_MSG_FILE_NAME, DEF_MAIN_BRANCH, DEF_PROJECT_PARENT_FOLDER, PIP_CMD, PROJECT_VERSION_SEP,
    PYPI_PACKAGE_NAMES, PYPI_ROOT_URL, PYPI_TEST_URL,
    TEST_PROJECTS_NAMESPACE, VERSION_MATCHER, VERSION_PREFIX, VERSION_QUOTE,
    code_file_title, code_file_version, code_version, get_pypi_versions, main_file_paths_parts, project_main_file,
    project_name_version, stripped_pip_name,
    PyMo)


@skip_gitlab_ci
def test_pip_names():
    pypi_root_url = f"https://pypi.org"  # == aedev.base.PYPI_ROOT_URL
    found_pip_names = set()
    for imp_name, pip_name in PYPI_PACKAGE_NAMES.items():
        assert imp_name

        assert pip_name
        assert not url_failure(f"{pypi_root_url}/project/{pip_name}/")
        assert pip_name.replace('.', '-').replace('_', '-').lower() == norm_pip_name(pip_name)

        pip_norm_name = norm_pip_name(pip_name)         # normalized pypi.org/project/<name>
        assert not url_failure(f"{pypi_root_url}/project/{pip_norm_name}")

        # prevent accidentally duplicated pip/pypi-Names (apart from the explicitly excluded extensions)
        assert (pip_norm_name not in found_pip_names
                or pip_name == 'pymongo' and imp_name in ('bson', 'gridfs')
                or pip_name == 'pywin32' and imp_name in ('win32api', 'win32com')
                or pip_name == 'django-cms' and imp_name in ('cms', 'menus')
                )
        found_pip_names.add(pip_norm_name)


class TestConstants:
    def test_declarations(self):
        assert APP_PRJ
        assert DJANGO_PRJ
        assert MODULE_PRJ
        assert NO_PRJ == ''
        assert PACKAGE_PRJ
        assert PARENT_PRJ
        assert PLAYGROUND_PRJ
        assert ROOT_PRJ
        assert COMMIT_MSG_FILE_NAME
        assert DEF_MAIN_BRANCH
        assert PIP_CMD
        assert PYPI_ROOT_URL
        assert PYPI_TEST_URL
        assert VERSION_MATCHER
        assert VERSION_PREFIX
        assert VERSION_QUOTE

    def test_project_types(self):
        assert isinstance(APP_PRJ, str)
        assert isinstance(DJANGO_PRJ, str)
        assert isinstance(MODULE_PRJ, str)
        assert isinstance(NO_PRJ, str)
        assert isinstance(PACKAGE_PRJ, str)
        assert isinstance(PARENT_PRJ, str)
        assert isinstance(PLAYGROUND_PRJ, str)
        assert isinstance(ROOT_PRJ, str)

    def test_project_type_groups(self):
        assert APP_PRJ in ANY_PRJ_TYPE

        assert NO_PRJ not in ANY_PRJ_TYPE
        assert PARENT_PRJ not in ANY_PRJ_TYPE

        assert APP_PRJ in ALL_PRJ_TYPES

        assert NO_PRJ in ALL_PRJ_TYPES
        assert PARENT_PRJ in ALL_PRJ_TYPES

    def test_version_matcher(self):
        assert isinstance(VERSION_MATCHER, re.Pattern)

        old_ver = VERSION_PREFIX + '888.999.000' + VERSION_QUOTE
        new_ver = VERSION_PREFIX + 'new-version' + VERSION_QUOTE
        prefix, suffix = f"{os.linesep}prefix{os.linesep}", f"  # comment {os.linesep}suffix{os.linesep}"
        old_str = prefix + old_ver + suffix

        new_str, cnt = VERSION_MATCHER.subn(new_ver, old_str)

        assert new_str == prefix + new_ver + suffix
        assert cnt == 1


class TestHelpers:
    def test_code_file_title(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_title.py')
        title_str = "this is an example of a code file title string"

        write_file(tst_file, f'''""" {title_str}\n\n    docstring body start here"""\n''')
        assert code_file_title(tst_file) == title_str

        write_file(tst_file, f'''"""\n{title_str}\n====================\n    docstring body start here"""\n''')
        assert code_file_title(tst_file) == title_str

    def test_code_file_title_invalid_file_content(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_title.py')
        write_file(tst_file, "")  # empty file
        assert not code_file_title(tst_file)

        write_file(tst_file, "\n\n this is no docstring and no title")  # invalid docstring/title
        assert not code_file_title(tst_file)

    def test_code_file_title_invalid_file_name(self):
        assert not code_file_title('::invalid_file_name::')

    def test_code_file_version(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_version.py')
        version_str = '33.22.111pre'
        write_file(tst_file, f"{VERSION_PREFIX}{version_str}{VERSION_QUOTE}  # comment\nversion = '9.6.3'")
        assert code_file_version(tst_file) == version_str

    def test_code_file_version_invalid_file_content(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_version.py')
        write_file(tst_file, "")  # empty file
        assert not code_file_version(tst_file)

        write_file(tst_file, "version__ = '1.2.3'")  # invalid version var prefix
        assert not code_file_version(tst_file)

    def test_code_file_version_invalid_file_name(self):
        assert not code_file_version('::invalid_file_name::')

    def test_code_version(self):
        version = '333.222.111dev'
        assert code_version(VERSION_PREFIX + version + VERSION_QUOTE) == version
        assert code_version(f"\n\n\n{VERSION_PREFIX}{version}{VERSION_QUOTE}\n\n\n") == version
        content = f"{VERSION_PREFIX}{version}{VERSION_QUOTE}  # comment\nversion = '9.6.3'"
        assert code_version(content) == version
        assert code_version(content.encode('utf-8')) == version

    def test_code_version_args(self):
        version = '999.333.111pre'
        assert code_version("    " + VERSION_PREFIX + version + VERSION_QUOTE) == ""
        assert code_version("    " + VERSION_PREFIX + version + VERSION_QUOTE, prefix=VERSION_PREFIX) == version

        assert code_version("\n\n    version: " + version, prefix="version: ", suffix="") == ""  # empty quote not valid
        assert code_version("\n\n    version: " + version, prefix="version: ", suffix="pre") == version[:-3]

    def test_code_version_errors(self):
        assert code_version("") == ""
        assert code_version("all but a  v-e_r.s;i:o,n") == ""

        # noinspection PyTypeChecker
        assert code_version(None) == ""

        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            assert code_version() == ""

    def test_get_pypi_versions(self):
        assert get_pypi_versions("") == [""]
        assert get_pypi_versions("non_existing_pypi_package") == [""]
        assert "0.3.54" in get_pypi_versions('ae_base')
        assert "0.3.81" in get_pypi_versions('ae_console')

        root_prj = f'{TEST_PROJECTS_NAMESPACE}_{TEST_PROJECTS_NAMESPACE}'
        assert "0.3.3" in get_pypi_versions(root_prj, pypi_test=True)   # force to use test domain test.pypi.org
        assert get_pypi_versions(root_prj, pypi_test=False) == [""]     # force to use live domain pypi.org

    def test_main_file_paths_parts(self):
        assert isinstance(main_file_paths_parts(""), tuple)
        assert len(main_file_paths_parts(""))
        assert isinstance(main_file_paths_parts("")[0], tuple)

        assert ('main' + '.py', ) in main_file_paths_parts("")
        assert any('__main__' + '.py' in _ for _ in main_file_paths_parts(""))
        assert any('__init__' + '.py' in _ for _ in main_file_paths_parts(""))

        por_name = "portion_tst_name"
        assert ('main' + '.py', ) in main_file_paths_parts(por_name)
        assert (por_name, '__init__' + '.py') in main_file_paths_parts(por_name)
        assert any(por_name in _ for _ in main_file_paths_parts(por_name))
        assert any(por_name + '.py' in _ for _ in main_file_paths_parts(por_name))

    def test_project_main_file(self, tmp_path):
        assert project_main_file("not_existing_xy.tst") == ""

        ae_system_main_file = norm_path(os_path_join('aedev', "base" + '.py'))
        assert project_main_file("aedev.base") == ae_system_main_file
        assert project_main_file("aedev.base", norm_path("")) == ae_system_main_file

        local_project_dir = os_path_join(str(tmp_path), "aedev_base")
        local_main_file = norm_path(os_path_join(local_project_dir, 'main' + '.py'))

        write_file(local_main_file, "# main file content", make_dirs=True)
        assert project_main_file("aedev.base") == ae_system_main_file
        assert project_main_file("aedev.base", norm_path("")) == ae_system_main_file
        assert project_main_file("aedev.base", local_project_dir) == local_main_file
        assert project_main_file("aedev.base", norm_path(local_project_dir)) == local_main_file

    def test_project_name_version(self):
        pkg, ver = project_name_version('', ['a_b', 'b_c'])
        assert pkg == ""
        assert ver == ""

        pkg, ver = project_name_version('x.z', [])
        assert pkg == ""
        assert ver == ""

        pkg, ver = project_name_version('x.z', ['a_b', 'b_c'])
        assert pkg == ""
        assert ver == ""

        pkg, ver = project_name_version('a.b', ['a_b', 'b_c'])
        assert pkg == 'a_b'
        assert ver == ""

        pkg, ver = project_name_version('a.b', ['bc', 'c_d', 'a_b==1.2.3'])
        assert pkg == 'a_b'
        assert ver == "1.2.3"

    def test_stripped_pip_name(self):
        assert stripped_pip_name("dot.name") == "dot-name"
        assert stripped_pip_name("under_name") == "under-name"
        assert stripped_pip_name("stripped-name") == "stripped-name"
        assert stripped_pip_name(f"name{PROJECT_VERSION_SEP}1.2.6") == "name"


class TestPyMo:
    def test_from_name(self):
        assert PyMo.from_name("") is not None
        # noinspection PyTypeChecker
        assert PyMo.from_name(None).import_name == 'import.name.error'
        assert PyMo.from_name("").import_name == 'import.name.error'
        assert PyMo.from_name("", namespace_name=".").import_name == 'import.name.error'
        assert PyMo.from_name("", namespace_name="tst").import_name == 'import.name.error'
        assert PyMo.from_name("", namespace_name="tst.name").import_name == 'import.name.error'

        assert (_mod := PyMo.from_name("imp.tst.name")) is not None
        assert _mod.import_name == "imp.tst.name"
        assert _mod.project_root_path == norm_path("imp_tst_name")

        assert (_mod := PyMo.from_name("imp.tst.name", namespace_name="imp")) is not None
        assert _mod.import_name == "imp.tst.name"
        assert _mod.project_root_path == norm_path("imp_tst_name")

        assert (_mod := PyMo.from_name("imp.tst.name", namespace_name="imp.tst")) is not None
        assert _mod.import_name == "imp.tst.name"
        assert _mod.project_root_path == norm_path("imp_tst_name")

        assert (_mod := PyMo.from_name("pip-tst-name")) is not None
        assert _mod.import_name == "pip_tst_name"
        assert _mod.project_root_path == norm_path("pip_tst_name")

        assert (_mod := PyMo.from_name("pip-tst-name", namespace_name="pip")) is not None
        assert _mod.import_name == "pip.tst_name"
        assert _mod.project_root_path == norm_path("pip_tst_name")

        assert (_mod := PyMo.from_name("pip-tst-name", namespace_name="pip.tst")) is not None
        assert _mod.import_name == "pip.tst.name"
        assert _mod.project_root_path == norm_path("pip_tst_name")

        assert (_mod := PyMo.from_name("pkg_tst_name")) is not None
        assert _mod.import_name == "pkg_tst_name"
        assert _mod.project_root_path == norm_path("pkg_tst_name")

        assert (_mod := PyMo.from_name("pkg_tst_name", namespace_name="pkg")) is not None
        assert _mod.import_name == "pkg.tst_name"
        assert _mod.project_root_path == norm_path("pkg_tst_name")

        assert (_mod := PyMo.from_name("pkg_tst_name", namespace_name="pkg.tst")) is not None
        assert _mod.import_name == "pkg.tst.name"
        assert _mod.project_root_path == norm_path("pkg_tst_name")

    @skip_gitlab_ci
    def test_from_path_local_src_packages(self):
        parent_dir = norm_path(f"~/{DEF_PROJECT_PARENT_FOLDER}")
        if os_path_isdir(_path := f"{parent_dir}/aedev_project_manager"):
            assert (_mod := PyMo.from_path(_path))  # w/o namespace_name argument!
            assert _mod.error_message == ""
            assert _mod.import_name == 'aedev.project_manager'
            assert isinstance(_mod.imported_module, ModuleType)
            assert isinstance(_mod.loaded_module, ModuleType)
            assert hasattr(_mod.loaded_module, '__path__')
            assert _mod.module_file_path == f"{parent_dir}/aedev_project_manager/aedev/project_manager{'.py'}"
            assert _mod.namespace_name == 'aedev'
            assert _mod.name_parts == ['aedev', 'project_manager']
            assert _mod.package_file_path == (f"{parent_dir}/aedev_project_manager/aedev/project_manager/"
                                              f"{'__init__' + '.py'}")
            assert _mod.package_name == "aedev_project_manager"
            assert _mod.pip_name == "aedev-project-manager"
            assert _mod.portion_name == 'project_manager'
            assert _mod.project_name == "aedev_project_manager"
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/aedev_project_manager"):
            assert (_mod := PyMo.from_path(_path, namespace_name='aedev'))
            assert _mod.error_message == ""
            assert _mod.import_name == 'aedev.project_manager'
            assert isinstance(_mod.imported_module, ModuleType)
            assert isinstance(_mod.loaded_module, ModuleType)
            assert hasattr(_mod.loaded_module, '__path__')
            assert _mod.module_file_path == f"{parent_dir}/aedev_project_manager/aedev/project_manager{'.py'}"
            assert _mod.namespace_name == 'aedev'
            assert _mod.name_parts == ['aedev', 'project_manager']
            assert _mod.package_file_path == (f"{parent_dir}/aedev_project_manager/aedev/project_manager/"
                                              f"{'__init__' + '.py'}")
            assert _mod.package_name == "aedev_project_manager"
            assert _mod.pip_name == "aedev-project-manager"
            assert _mod.portion_name == 'project_manager'
            assert _mod.project_name == "aedev_project_manager"
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/aedev_project_vars"):
            assert (_mod := PyMo.from_path(_path))  # w/o namespace_name arg
            assert _mod.error_message == ""
            assert _mod.import_name == 'aedev.project_vars'
            assert _mod.module_file_path == f"{parent_dir}/aedev_project_vars/aedev/project_vars{'.py'}"
            assert _mod.namespace_name == 'aedev'
            assert _mod.name_parts == ['aedev', 'project_vars']
            assert _mod.package_file_path == (f"{parent_dir}/aedev_project_vars/aedev/project_vars/"
                                              f"{'__init__' + '.py'}")
            assert _mod.portion_name == 'project_vars'
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/aedev_project_vars"):
            assert (_mod := PyMo.from_path(_path, namespace_name='aedev'))
            assert _mod.error_message == ""
            assert _mod.import_name == 'aedev.project_vars'
            assert _mod.module_file_path == f"{parent_dir}/aedev_project_vars/aedev/project_vars{'.py'}"
            assert _mod.namespace_name == 'aedev'
            assert _mod.name_parts == ['aedev', 'project_vars']
            assert _mod.package_file_path == (f"{parent_dir}/aedev_project_vars/aedev/project_vars/"
                                              f"{'__init__' + '.py'}")
            assert _mod.portion_name == 'project_vars'
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/glsl_tester"):
            assert (_mod := PyMo.from_path(_path))
            assert _mod.error_message == ""
            assert _mod.import_name == 'glsl_tester'
            assert _mod.module_file_path == f"{parent_dir}/glsl_tester/glsl_tester{'.py'}"
            assert _mod.namespace_name == ''
            assert _mod.name_parts == ["glsl_tester"]
            assert _mod.package_name == 'glsl_tester'
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/oaio_server"):
            assert (_mod := PyMo.from_path(_path))
            assert _mod.error_message == ""
            assert _mod.import_name == 'oaio_server'
            assert _mod.namespace_name == ''
            assert _mod.name_parts == ["oaio_server"]
            assert _mod.package_name == "oaio_server"
            assert _mod.project_root_path == _path

        if os_path_isdir(_path := f"{parent_dir}/kairos"):
            assert (_mod := PyMo.from_path(_path))
            assert _mod.error_message == ""
            assert _mod.import_name == 'kairos'
            assert _mod.namespace_name == ''
            assert _mod.name_parts == ["kairos"]
            assert _mod.project_root_path == _path

    def test_from_path_not_existing(self):
        assert PyMo.from_path("") is not None
        assert PyMo.from_path("").import_name == 'aedev.base'
        assert PyMo.from_path("", namespace_name=".") is not None
        assert PyMo.from_path("", namespace_name="namespacename") is not None
        assert PyMo.from_path("", namespace_name="namespace.name") is not None
        assert PyMo.from_path("", namespace_name="namespace-name") is not None
        assert PyMo.from_path("", namespace_name="namespace_name") is not None

        assert (_mod := PyMo.from_path("not_existing_project_dir")) is not None
        assert _mod.import_name == "not_existing_project_dir"

        assert (_mod := PyMo.from_path("not_existing_project_dir", namespace_name="not.existing")) is not None
        assert _mod.import_name == "not.existing.project_dir"

        assert PyMo.from_path("~/_not_existing") is not None

    def test_pymo_class_and_instance(self):
        assert PyMo("").__class__ is PyMo
        assert PyMo("")
        assert PyMo("xy_abc")
        assert PyMo("a.b.c")

    def test_imported_module_ae_base(self):
        mod_ref = PyMo('ae.base').imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'write_file') == write_file

    def test_imported_module_built_ins(self):
        assert isinstance(PyMo('os').imported_module, ModuleType)
        assert isinstance(PyMo('os.path').imported_module, ModuleType)
        assert isinstance(PyMo('textwrap').imported_module, ModuleType)

    def test_imported_module_local_module(self, monkeypatch, tmp_path):
        module = "mod_2_tst"
        mod_file = os_path_join(str(tmp_path), module + '.py')
        write_file(mod_file, "mod_var = 'mod_var_val'")

        assert PyMo(module).imported_module is None

        assert PyMo(module, project_path=str(tmp_path)).imported_module is None

        assert PyMo(os_path_basename(str(tmp_path)) + '.' + module).imported_module is None

        monkeypatch.chdir(str(tmp_path))

        assert PyMo(module, project_path=module + '.py').imported_module is None

        assert PyMo(module).imported_module is None

        monkeypatch.syspath_prepend(str(tmp_path))

        mod_ref = PyMo(module, project_path=mod_file).imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        monkeypatch.syspath_prepend(os_path_dirname(str(tmp_path)))

        mod_ref = PyMo(os_path_basename(str(tmp_path)) + '.' + module).imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

    def test_imported_module_local_package(self, monkeypatch, tmp_path):
        namespace = "z_y"
        portion = "por_2_tst"
        pkg_root = os_path_join(str(tmp_path), namespace)
        pkg_path = os_path_join(pkg_root, portion)
        pkg_file = os_path_join(pkg_path, '__init__' + '.py')
        write_file(pkg_file, "pkg_var = 'pkg_var_val'", make_dirs=True)

        assert PyMo(namespace + '.' + portion).imported_module is None

        assert PyMo(portion).loaded_module is None

        assert PyMo(portion, project_path=pkg_root).imported_module is None

        assert PyMo(portion, project_path=pkg_file).imported_module is None

        assert PyMo(namespace + '.' + portion, project_path=os_path_dirname(pkg_root)).imported_module is None

        assert PyMo(str(tmp_path) + '.' + namespace + '.' + portion, project_path=pkg_root).imported_module is None

        assert PyMo(str(tmp_path) + '.' + namespace + '.' + portion).imported_module is None

        monkeypatch.chdir(str(tmp_path))

        assert PyMo(namespace + '.' + portion).imported_module is None

        assert PyMo(namespace + '.' + portion,
                    project_path=os_path_relpath(pkg_file, str(tmp_path))).imported_module is None

        monkeypatch.syspath_prepend(str(tmp_path))

        mod_ref = PyMo(namespace + '.' + portion).imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(namespace + '.' + portion, project_path="any_path").imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        monkeypatch.syspath_prepend(os_path_dirname(str(tmp_path)))

        mod_ref = PyMo(namespace + '.' + portion).imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(namespace + '.' + portion, project_path=os_path_relpath(pkg_file, str(tmp_path))).imported_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

    def test_imported_module_not_exists(self):
        assert PyMo('not_existing_import_name').imported_module is None

    def test_loaded_module_aedev_base(self):
        mod_ref = PyMo('aedev.base').loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'PACKAGE_PRJ') == PACKAGE_PRJ

    def test_loaded_module_built_ins(self):
        assert isinstance(PyMo('os').loaded_module, ModuleType)
        assert isinstance(PyMo('textwrap').loaded_module, ModuleType)

    def test_loaded_module_local_module(self, monkeypatch, tmp_path):
        module = "mod_2_tst"
        mod_file = os_path_join(str(tmp_path), module + '.py')
        write_file(mod_file, "mod_var = 'mod_var_val'")

        assert PyMo(module + '.py').loaded_module is None

        mod_ref = PyMo(module).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = PyMo(module, project_path=os_path_dirname(mod_file)).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = PyMo(os_path_basename(str(tmp_path)) + '.' + module,
                       project_path=os_path_dirname(str(tmp_path))).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = PyMo(str(tmp_path) + '.' + module).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        monkeypatch.chdir(str(tmp_path))

        mod_ref = PyMo(module, project_path=module + '.py').loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = PyMo(module).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

    def test_loaded_module_local_package(self, monkeypatch, tmp_path):
        namespace = "n_s"
        portion = "por_2_tst"
        pkg_root = os_path_join(str(tmp_path), namespace)
        pkg_path = os_path_join(pkg_root, portion)
        pkg_file = os_path_join(pkg_path, '__init__' + '.py')
        write_file(pkg_file, "pkg_var = 'pkg_var_val'", make_dirs=True)

        assert PyMo(namespace + '.' + portion).loaded_module is None

        assert PyMo(portion).loaded_module is None

        mod_ref = PyMo(portion, project_path=pkg_root).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(namespace + '.' + portion, project_path=os_path_dirname(pkg_root)).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(str(tmp_path) + '.' + namespace + '.' + portion, project_path=pkg_root).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(str(tmp_path) + '.' + namespace + '.' + portion).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        monkeypatch.chdir(str(tmp_path))

        mod_ref = PyMo(namespace + '.' + portion).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = PyMo(namespace + '.' + portion, project_path=os_path_relpath(pkg_file, str(tmp_path))).loaded_module
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

    def test_loaded_module_not_exists(self):
        assert PyMo('not_existing_import_name').loaded_module is None

    def test_module_file_path(self):
        mod = PyMo("tst_nam")
        assert mod.module_file_path == "tst_nam" + '.py'

        mod = PyMo("tst_nam", project_path="prj_path")
        assert mod.module_file_path == os_path_join("prj_path", "tst_nam" + '.py')

        mod = PyMo("tst.nam", project_path="prj_path")
        assert mod.module_file_path == os_path_join("prj_path", "tst", "nam" + '.py')

    def test_namespace_guess_module_portion(self, tmp_path):
        namespace = 'z_y'
        portion_name = 'portion_name'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = namespace + "_" + portion_name
        project_path = os_path_join(parent_dir, project_name)
        namespace_dir = os_path_join(project_path, namespace)
        main_file = os_path_join(namespace_dir, portion_name + '.py')
        write_file(main_file, "# main file of module portion", make_dirs=True)

        assert PyMo.from_path(project_path).namespace_name == namespace

    def test_namespace_guess_package_portion(self, tmp_path):
        namespace = 'x_y'
        portion_name = 'portion_name'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = namespace + "_" + portion_name
        project_path = os_path_join(parent_dir, project_name)
        namespace_dir = os_path_join(project_path, namespace)
        portion_dir = os_path_join(namespace_dir, portion_name)
        main_file = os_path_join(portion_dir, '__init__' + '.py')
        write_file(main_file, "# main file of package portion", make_dirs=True)

        assert PyMo.from_path(project_path).namespace_name == namespace

    def test_namespace_guess_project_at_cwd(self):
        assert PyMo.from_path("").namespace_name == 'aedev'
        assert PyMo.from_path(os.getcwd()).namespace_name == 'aedev'

    def test_namespace_guess_root(self, tmp_path):
        namespace = 'x_z'
        parent_dir = os_path_join(tmp_path, DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, namespace + "_" + namespace)
        main_file = os_path_join(project_path, namespace + '.py')
        write_file(main_file, "# main file of non-namespace module", make_dirs=True)

        assert not PyMo.from_path(project_path).namespace_name

        os.remove(main_file)

        main_file = os_path_join(project_path, 'main' + '.py')
        write_file(main_file, "# main file of non-namespace project")

        assert PyMo.from_path(project_path).namespace_name == ""

        os.remove(main_file)

        main_file = os_path_join(project_path, '__init__' + '.py')
        write_file(main_file, "# main file of non-namespace package")

        assert PyMo.from_path(project_path).namespace_name == ""

        os.remove(main_file)

        por_dir = os_path_join(project_path, namespace)
        main_file = os_path_join(por_dir, namespace + '.py')
        write_file(main_file, "# main file of namespace root module", make_dirs=True)

        assert PyMo.from_path(project_path).namespace_name == namespace

        os.remove(main_file)

        main_file = os_path_join(por_dir, 'main' + '.py')
        write_file(main_file, "# main file of namespace root main")

        assert PyMo.from_path(project_path).namespace_name == namespace

        os.remove(main_file)

        por_dir = os_path_join(por_dir, namespace)   # == os_path_join(project_path, namespace, namespace)
        main_file = os_path_join(por_dir, '__init__' + '.py')
        write_file(main_file, "# main file of namespace root package", make_dirs=True)

        assert PyMo.from_path(project_path).namespace_name == namespace

    def test_namespace_guess_sub_module(self):
        assert PyMo.from_path('ae') is not None
        assert PyMo.from_path('ae').namespace_name == ""

        assert PyMo.from_path("not_existing") is not None
        assert PyMo.from_path("not_existing").namespace_name == ""

    def test_namespace_guess_with_underscore(self, tmp_path):
        namespace = 'n_x'
        parent_dir = os_path_join(tmp_path, DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, namespace + "_" + namespace)
        por_dir = os_path_join(project_path, namespace, namespace)
        write_file(os_path_join(por_dir, '__init__' + '.py'), "# main file of non-namespace module", make_dirs=True)

        assert PyMo.from_path(project_path).namespace_name == namespace

    def test_package_file_path(self):
        mod = PyMo("tst_nam")
        assert mod.package_file_path == os_path_join("tst_nam", '__init__' + '.py')

        mod = PyMo("tst_nam", project_path="prj_path")
        assert mod.package_file_path == os_path_join("prj_path", "tst_nam", '__init__' + '.py')

        mod = PyMo("tst.nam", project_path="prj_path")
        assert mod.package_file_path == os_path_join("prj_path", "tst", "nam", '__init__' + '.py')

    def test_pip_name(self):
        mod = PyMo("tst_nam")
        assert mod.pip_name == "tst-nam"

        mod = PyMo("tst.nam")
        assert mod.pip_name == "tst-nam"

        mod = PyMo('PIL')
        assert mod.pip_name == "pillow"

        mod = PyMo("tst.nam", **{"tst.nam": "Irregular-Name"})
        assert mod.project_name == "Irregular-Name"

    def test_portion_name(self):
        mod = PyMo("tst_nam")
        assert mod.portion_name == "tst_nam"

        mod = PyMo("tst.nam")
        assert mod.portion_name == "nam"

    def test_project_name(self):
        mod = PyMo("tst_nam")
        assert mod.project_name == "tst_nam"

        mod = PyMo('PIL')
        assert mod.project_name == "pillow"

        mod = PyMo('PIL', **{'PIL': 'PIL'})
        assert mod.project_name == "PIL"

        mod = PyMo('PIL', PIL='PIL')
        assert mod.project_name == "PIL"

        mod = PyMo('PIL')       # test that the default value of PIL did not get overwritten
        assert mod.project_name == "pillow"

        mod = PyMo('namespace.mod', **{"namespace.mod": "Irr-Nam-Mod"})
        assert mod.project_name == "Irr-Nam-Mod"

    def test_pypi_names(self):
        pypi_names = {'tst.pypi.nam': 'Irr-Name', 'PIP': 'New-Pip'}

        mod = PyMo('tst.pypi.nam', **pypi_names)
        assert mod.project_name == pypi_names['tst.pypi.nam']
        assert mod.pip_name == pypi_names['tst.pypi.nam'].lower()

        mod = PyMo('PIP', **pypi_names)
        assert mod.project_name == pypi_names['PIP']
        assert mod.pip_name == pypi_names['PIP'].lower()

    def test_repr(self):
        mod = PyMo("any_name")
        assert repr(mod).startswith("PyMo('any_name'")
