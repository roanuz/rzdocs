from .webapp import run_preview
from .buildpreview import run_buildpreview
from .build_html import run_build
import click


__version__ = '1.0.0.3'


@click.group()
def app():
    pass


@app.command()
def preview():
    run_preview()


@app.command()
@click.argument('name', default='')
def json_preview(name):
    if not name:
        name = None
    run_buildpreview(name)


@app.command()
def build():
    run_build()


if __name__ == '__main__':
    app()
