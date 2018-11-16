import os
from flask import Flask, render_template, Blueprint, send_from_directory
from .build import generate_html, build_menu

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
    template = '2col.html'

    if path.startswith('.') or path.startswith('/'):
        return "Invalid path", 403

    menu, page = build_menu(path)
    if page is None:
        return "Page not Found!", 404

    if page.use_auto_index and page.is_index_page:
        webpage = page.index_webpage()
        template = 'index.html'
    else:
        webpage = generate_html(page.file_path)

    if webpage.template:
        template = webpage.template
    elif page.template:
        template = page.template
    elif menu.default_template and (not page.is_index_page):
        template = menu.default_template

    if not template.endswith('.html'):
        template = template + '.html'

    desc = webpage.desc

    if desc is None and page.meta:
        desc = page.meta.get('desc', None)

    if isinstance(webpage, tuple):
        return webpage

    title = page.name if webpage.title is None else webpage.title
    # visible_to = page.visible_to if webpage.visible_to is None else webpage.visible_to

    return render_template(
        template,
        page_content=webpage.content,
        menu=menu,
        page=page,
        webpage=webpage,
        title=title,
        page_description=desc
    )


def run_preview():
    app.run(host="0.0.0.0", debug=True)
