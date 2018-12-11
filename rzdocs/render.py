from flask import render_template
from .build import build_webtree_page, build_webtree_page_json


def render_doc_from_html(path):
    if path.startswith('.') or path.startswith('/'):
        return "Invalid path", 403

    tree_page = build_webtree_page(path)
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


def render_doc_from_json(path, base_path, template_base_path=None, context=None):
    if path.startswith('.') or path.startswith('/'):
        return "Invalid path", 403

    tree_page = build_webtree_page_json(path, base_path)
    # print(tree_page.webpage)

    if isinstance(tree_page.error, tuple):
        return tree_page.error

    if (tree_page.webpage is None):
        return "Page not Found!", 404

    if context is None:
        context = {}

    template = tree_page.webpage.template
    if template_base_path is not None:
        template = template_base_path + '/' + template

    return render_template(
        template,
        tree_page=tree_page,

        webtree=tree_page.tree,
        child=tree_page.child,
        webpage=tree_page.webpage,

        page_content=tree_page.webpage.content,
        title=tree_page.webpage.title,
        page_description=tree_page.webpage.desc,
        **context
    )
