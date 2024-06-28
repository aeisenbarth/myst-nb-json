# MyST-NB JSON

A MIME-type plugin for rendering JSON output from Jupyter notebooks to HTML

______________________________________________________________________

```{toctree}
:hidden:

examples
development
```

Outputs from Jupyter notebook code cells usually contain representations in one or multiple MIME
types (image, text…). IPython provides multiple built-in output types, but not all of them
have a representation for HTML, and fall back to a stringified version of the Python object.

This is the case for the `application/json` type:

It is nicely rendered in Jupyter because Jupyter includes a
[JSON renderer](https://github.com/jupyterlab/jupyterlab/tree/7909745d075aceb0cf1099ad53a3174e92b575ae/packages/json-extension),
but [MyST-NB](https://myst-nb.readthedocs.io) can only use IPython's built-ins which display as
`<IPython.core.display.JSON object>`.

## Installation

Make sure `Sphinx` and `myst-nb` are installed, this package is meant to be used with them.

Install the Python package:

```shell
pip install myst-nb-json
```

It registers itself in MyST-NB via entry-points, so it is ready to use.

## Usage

1. Wrap output from code cells in the IPython `JSON` class.

   ```python
   from IPython.display import JSON

   JSON({"key": "value"})
   ```

2. When building documentation with Sphinx, the JSON output will be rendered as interactive tree,
   instead of displaying plain text.

   ```shell
   sphinx-build -b html docs/ docs/_build
   ```

   Or just the notebook with:

   ```shell
   mystnb-docutils-html example.ipynb > example.html
   ```

For more details, see [examples](./examples.ipynb).
