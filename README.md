# MyST-NB JSON

A MIME-type plugin for rendering JSON output from Jupyter notebooks to HTML

______________________________________________________________________

Outputs from Jupyter notebook code cells usually contain representations in one or multiple MIME
types (image, text…). IPython provides multiple built-in output types, but not all of them
have a representation for HTML, and fall back to a stringified version of the Python object.

This is the case for the `application/json` type:

It is nicely rendered in Jupyter because Jupyter includes a
[JSON renderer](https://github.com/jupyterlab/jupyterlab/tree/7909745d075aceb0cf1099ad53a3174e92b575ae/packages/json-extension),
but [MyST-NB](https://myst-nb.readthedocs.io) can only use IPython's built-ins which display as
`<IPython.core.display.JSON object>`.

## Jupyter Lab

![Screenshot of json_dict in Jupyter](./docs/images/example1-jupyter.png)

## MyST-NB without plugin

![Screenshot of json_dict in HTML by MyST-NB](./docs/images/example1-myst-nb.png)

## MyST-NB with myst-nb-json plugin

![Screenshot of json_dict in HTML with myst-nb-json](./docs/images/example1-myst-nb-json.png)
