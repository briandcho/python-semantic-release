import os
import platform
from textwrap import dedent

import pytest

from semantic_release.errors import ImproperConfigurationError
from semantic_release.history import parser_angular
from semantic_release.settings import _config, current_commit_parser

from . import mock, reset_config

assert reset_config


# Set path to this directory
temp_dir = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")
    if platform.system() == "Windows"
    else "/tmp/"
)


def test_config():
    config = _config()
    assert config.get("version_variable") == "semantic_release/__init__.py:__version__"


@mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
def test_defaults(mock_getcwd):
    config = _config()
    mock_getcwd.assert_called_once_with()
    assert config.get("minor_tag") == ":sparkles:"
    assert config.get("fix_tag") == ":nut_and_bolt:"
    assert not config.get("patch_without_tag")
    assert config.get("major_on_zero")
    assert not config.get("check_build_status")
    assert config.get("hvcs") == "github"
    assert config.get("upload_to_repository") == True
    assert config.get("github_token_var") == "GH_TOKEN"
    assert config.get("gitea_token_var") == "GITEA_TOKEN"
    assert config.get("gitlab_token_var") == "GL_TOKEN"
    assert config.get("pypi_pass_var") == "PYPI_PASSWORD"
    assert config.get("pypi_token_var") == "PYPI_TOKEN"
    assert config.get("pypi_user_var") == "PYPI_USERNAME"
    assert config.get("repository_user_var") == "REPOSITORY_USERNAME"
    assert config.get("repository_pass_var") == "REPOSITORY_PASSWORD"


@mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
def test_toml_override(mock_getcwd):
    # create temporary toml config file
    dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
    os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
    toml_conf_content = """
[tool.foo]
bar = "baz"
[tool.semantic_release]
upload_to_repository = false
version_source = "tag"
foo = "bar"
"""
    with open(dummy_conf_path, "w") as dummy_conf_file:
        dummy_conf_file.write(toml_conf_content)

    config = _config()
    mock_getcwd.assert_called_once_with()
    assert config.get("hvcs") == "github"
    assert config.get("upload_to_repository") == False
    assert config.get("version_source") == "tag"
    assert config.get("foo") == "bar"

    # delete temporary toml config file
    os.remove(dummy_conf_path)


@mock.patch("semantic_release.settings.logger.warning")
@mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
def test_no_raise_toml_error(mock_getcwd, mock_warning):
    # create temporary toml config file
    dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
    bad_toml_conf_content = """\
    TITLE OF BAD TOML
    [section]
    key = # BAD BECAUSE NO VALUE
    """
    os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)

    with open(dummy_conf_path, "w") as dummy_conf_file:
        dummy_conf_file.write(bad_toml_conf_content)

    _ = _config()
    mock_getcwd.assert_called_once_with()
    mock_warning.assert_called_once_with(
        'Could not decode pyproject.toml: Invalid key "TITLE OF BAD TOML" at line 1 col 21'
    )
    # delete temporary toml config file
    os.remove(dummy_conf_path)


@mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
def test_toml_no_psr_section(mock_getcwd):
    # create temporary toml config file
    dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
    toml_conf_content = dedent(
        """
        [tool.foo]
        bar = "baz"
        """
    )
    os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)

    with open(dummy_conf_path, "w") as dummy_conf_file:
        dummy_conf_file.write(toml_conf_content)

    config = _config()
    mock_getcwd.assert_called_once_with()
    assert config.get("hvcs") == "github"
    # delete temporary toml config file
    os.remove(dummy_conf_path)


@mock.patch("semantic_release.settings.config.get", lambda *x: "nonexistent.parser")
def test_current_commit_parser_should_raise_error_if_parser_module_do_not_exist():
    with pytest.raises(ImproperConfigurationError):
        current_commit_parser()


@mock.patch(
    "semantic_release.settings.config.get",
    lambda *x: "semantic_release.not_a_parser",
)
def test_current_commit_parser_should_raise_error_if_parser_do_not_exist():
    with pytest.raises(ImproperConfigurationError):
        current_commit_parser()


def test_current_commit_parser_should_return_correct_parser():
    assert current_commit_parser() == parser_angular.parse_commit_message
