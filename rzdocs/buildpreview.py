import os
from flask import Flask, Blueprint, send_from_directory
from .render import render_doc_from_json

app_path = path = os.path.dirname(os.path.abspath(__file__))
app = Flask('rzdocs_preview', static_url_path='/_static', root_path=app_path)

blueprint = Blueprint('md_media', 'md_media', static_url_path='/media', static_folder='media')
app.register_blueprint(blueprint)

build_configs = dict(all=[], main=None)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>/')
def home(path=None):
    return render_doc_from_json(path, base_path=build_configs['main'].dist_folder)


def run_buildpreview(config_name=None):
    from .build_html import load_config
    if build_configs['main'] is None and (config_name is not None):
        found = False
        configs = load_config()
        build_configs['all'] = configs
        for config in configs:
            if config.name == config_name:
                found = True
                build_configs['main'] = config
                print('Preview from', config.dist_folder)
                break

        if not found:
            print('Config not found. Available configs are ', ', '.join([c.name for c in configs]))
            return

    app.run(host="0.0.0.0", debug=True)
