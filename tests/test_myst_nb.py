import pytest

from tests.conftest import clean_doctree, file_regression, get_test_path, sphinx_run  # noqa: F401


@pytest.mark.sphinx_params("json_output.ipynb", conf={"nb_execution_mode": "force"})
def test_render_json_output(
    sphinx_run,  # noqa: F811
    clean_doctree,  # noqa: F811
    file_regression,  # noqa: F811
    get_test_path,  # noqa: F811
):
    """Test that a cell with JSON output is rendered with the MIME type plugin"""
    sphinx_run.build()
    assert sphinx_run.warnings() == ""
    doctree = clean_doctree(sphinx_run.get_resolved_doctree("json_output"))
    file_regression.check(doctree.pformat(), extension=".xml", encoding="utf-8")
