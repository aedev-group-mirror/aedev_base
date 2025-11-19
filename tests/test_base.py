""" aedev.base unit tests """
import os
import re
import pytest

from ae.base import os_path_join, write_file

from aedev.base import (
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, PLAYGROUND_PRJ, ROOT_PRJ,
    ANY_PRJ_TYPE, ALL_PRJ_TYPES,
    COMMIT_MSG_FILE_NAME, DEF_MAIN_BRANCH, PIP_CMD, PIP_INSTALL_CMD, PYPI_ROOT_URL, PYPI_ROOT_URL_TEST,
    VERSION_MATCHER, VERSION_PREFIX, VERSION_QUOTE,
    code_file_title, code_file_version, code_version, get_pypi_versions, project_name_version)


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
        assert PIP_INSTALL_CMD
        assert PYPI_ROOT_URL
        assert PYPI_ROOT_URL_TEST
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

        write_file(tst_file, f'''""" {title_str}\n\n    docstring body start here..."""\n''')
        assert code_file_title(tst_file) == title_str

        write_file(tst_file, f'''"""\n{title_str}\n====================\n    docstring body start here..."""\n''')
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

        assert "0.3.3" in get_pypi_versions('aetst_aetst', pypi_test=True)  # force to use test domain test.pypi.org
        assert get_pypi_versions('aetst_aetst', pypi_test=False) == [""]    # force to use live domain pypi.org

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
