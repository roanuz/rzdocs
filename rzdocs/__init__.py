from .webapp import run_preview
import click


__version__ = '1.0.0.3'


@click.group()
def app():
    pass


@app.command()
def preview():
    run_preview()


if __name__ == '__main__':
    app()