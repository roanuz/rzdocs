import os
from flask import Flask, Blueprint, send_from_directory
from .render import render_doc_from_html

app_path = path = os.path.dirname(os.path.abspath(__file__))
app = Flask('rzdocs_preview', static_url_path='/_static', root_path=app_path)

blueprint = Blueprint('md_media', 'md_media', static_url_path='/media', static_folder='media')
app.register_blueprint(blueprint)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>/')
def home(path=None):
    return render_doc_from_html(path)


def run_preview():
    app.run(host="0.0.0.0", debug=True)
