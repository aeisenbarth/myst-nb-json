# Source: https://github.com/executablebooks/MyST-NB/blob/master/tests/conftest.py
import json
import os
import re
import uuid
from pathlib import Path

import pytest
import sphinx
from docutils.nodes import image as image_node
from sphinx import version_info as sphinx_version_info
from sphinx.util.console import nocolor

pytest_plugins = "sphinx.testing.fixtures"

TEST_FILE_DIR = Path(__file__).parent.joinpath("notebooks")


@pytest.fixture()
def get_test_path():
    def _get_test_path(name):
        return TEST_FILE_DIR.joinpath(name)

    return _get_test_path


class SphinxFixture:
    """A class returned by the ``sphinx_run`` fixture, to run sphinx,
    and retrieve aspects of the build.
    """

    def __init__(self, app, filenames):
        self.app = app
        self.env = app.env
        self.files = [os.path.splitext(ff) for ff in filenames]
        self.software_versions = (
            f".sphinx{sphinx.version_info[0]}"  # software version tracking for fixtures
        )

    def build(self):
        """Run the sphinx build."""
        self.app.build()

    def warnings(self):
        """Return the stderr stream of the sphinx build."""
        return self.app._warning.getvalue().strip()

    def get_resolved_doctree(self, docname=None):
        """Load and return the built docutils.document, after post-transforms."""
        docname = docname or self.files[0][0]
        doctree = self.env.get_and_resolve_doctree(docname, self.app.builder)
        doctree["source"] = docname
        return doctree


@pytest.fixture()
def sphinx_params(request):
    """Parameters that are specified by 'pytest.mark.sphinx_params'
    are passed to the ``sphinx_run`` fixture::

        @pytest.mark.sphinx_params("name.ipynb", conf={"option": "value"})
        def test_something(sphinx_run):
            ...

    The first file specified here will be set as the master_doc
    """
    markers = request.node.iter_markers("sphinx_params")
    kwargs = {}
    if markers is not None:
        for info in reversed(list(markers)):
            kwargs.update(info.kwargs)
            kwargs["files"] = info.args
    return kwargs


@pytest.fixture()
def sphinx_run(sphinx_params, make_app, tmp_path):
    """A fixture to setup and run a sphinx build, in a sandboxed folder.

    The `myst_nb` extension is added by default,
    and the first file will be set as the masterdoc

    """
    assert len(sphinx_params["files"]) > 0, sphinx_params["files"]
    conf = sphinx_params.get("conf", {})
    buildername = sphinx_params.get("buildername", "html")

    confoverrides = {
        "extensions": ["myst_nb"],
        "master_doc": os.path.splitext(sphinx_params["files"][0])[0],
        "exclude_patterns": ["_build"],
        "nb_execution_show_tb": True,
    }
    confoverrides.update(conf)

    current_dir = os.getcwd()
    if "working_dir" in sphinx_params:
        base_dir = Path(sphinx_params["working_dir"]) / str(uuid.uuid4())
    else:
        base_dir = tmp_path
    srcdir = base_dir / "source"
    srcdir.mkdir(exist_ok=True)
    os.chdir(base_dir)
    (srcdir / "conf.py").write_text(
        "# conf overrides (passed directly to sphinx):\n"
        + "\n".join(["# " + ll for ll in json.dumps(confoverrides, indent=2).splitlines()])
        + "\n"
    )

    for nb_file in sphinx_params["files"]:
        nb_path = TEST_FILE_DIR.joinpath(nb_file)
        assert nb_path.exists(), nb_path
        (srcdir / nb_file).parent.mkdir(exist_ok=True)
        (srcdir / nb_file).write_text(nb_path.read_text(encoding="utf-8"), encoding="utf-8")

    nocolor()

    # For compatibility with multiple versions of sphinx, convert pathlib.Path to
    # sphinx.testing.path.path here.
    if sphinx_version_info >= (7, 2):
        app_srcdir = srcdir
    else:
        from sphinx.testing.path import path

        app_srcdir = path(os.fspath(srcdir))
    app = make_app(buildername=buildername, srcdir=app_srcdir, confoverrides=confoverrides)

    yield SphinxFixture(app, sphinx_params["files"])

    # reset working directory
    os.chdir(current_dir)


@pytest.fixture()
def clean_doctree():
    def _func(doctree):
        if os.name == "nt":  # on Windows file paths are absolute
            findall = getattr(doctree, "findall", doctree.traverse)
            for node in findall(image_node):  # type: image_node
                if "candidates" in node:
                    node["candidates"]["*"] = "_build/jupyter_execute/" + os.path.basename(
                        node["candidates"]["*"]
                    )
                if "uri" in node:
                    node["uri"] = "_build/jupyter_execute/" + os.path.basename(node["uri"])
        return doctree

    return _func


@pytest.fixture()
def file_regression(file_regression):
    return FileRegression(file_regression)


class FileRegression:
    ignores = (r"<script>.*</script>",)

    def __init__(self, file_regression):
        self.file_regression = file_regression

    def check(self, data, **kwargs):
        return self.file_regression.check(self._strip_ignores(data), **kwargs)

    def _strip_ignores(self, data):
        for ig in self.ignores:
            data = re.sub(ig, "", data)
        return data
