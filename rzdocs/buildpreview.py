import os
import click
from flask import Flask, render_template, Blueprint, send_from_directory, g
from .build import generate_html, build_webtree_page_json

app_path = path = os.path.dirname(os.path.abspath(__file__))
app = Flask('rzdocs_preview', static_url_path='/_static', root_path=app_path)

@app.before_first_request
def app_init():
    config = build_configs['main']
    print('Preview from', config.dist_folder)
    os.chdir(config.dist_folder)


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
    if path.startswith('.') or path.startswith('/'):
        return "Invalid path", 403

    tree_page = build_webtree_page_json(path)
    # print(tree_page.webpage)

    if isinstance(tree_page.error, tuple):
        return tree_page.error

    if (tree_page.webpage is None):
        return "Page not Found!", 404

    return render_template(
        tree_page.webpage.template,
        tree_page=tree_page,

        webtree=tree_page.tree,
        child=tree_page.child,
        webpage=tree_page.webpage,

        page_content=tree_page.webpage.content,
        title=tree_page.webpage.title,
        page_description=tree_page.webpage.desc
    )


def run_buildpreview(config_name=None):
    from .build_html import load_config
    if build_configs['main'] is None and (config_name is not None):
        found = False
        configs = load_config()
        build_configs['all'] = configs
        for config in configs:
            if config.name == config_name:
                # os.chdir(config.src_folder)
                found = True
                build_configs['main'] = config
                break

        if not found:
            print('Config not found. Available configs are ', ', '.join([c.name for c in configs]))
            return

    app.run(host="0.0.0.0", debug=True)
