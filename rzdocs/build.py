from pathlib import Path
from .page import WebTree, WebPage, WebTreeAndPageResponse
import yaml
import json
import markdown
import shutil


def get_md_class():
    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        'markdown.extensions.fenced_code',
        'markdown.extensions.attr_list',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown_include.include',
        ])

    return md


def build_root_webtree():
    raw = ''
    path = Path('.')
    filename = 'webtree.yaml'

    if (path / filename).exists():
        yfile = path / filename
        with yfile.open() as fs:
            raw = yaml.load(fs)

    return WebTree.from_dict(raw, use_as_menu=True)


class TreeCache:
    root_tree = {}


def build_webtree_page_json(path_str, base_path):
    if isinstance(base_path, str):
        base_path = Path(base_path)

    if TreeCache.root_tree.get(base_path) is None:
        tree_path = base_path / '_tree.json'
        with open(tree_path) as file:
            TreeCache.root_tree[base_path] = WebTree.from_json(json.load(file))

    path = base_path / Path(path_str)
    abs_url = path_str
    if abs_url:
        abs_url = '/{}/'.format(abs_url)

    root_webtree = TreeCache.root_tree.get(base_path)
    webtree = None
    webpage = None
    child = root_webtree.find_child(abs_url)
    error = None

    if child is not None:
        parent = child.find_menu(root_webtree)
        if parent is not None:
            webtree = parent

        if path.exists() and path.is_dir():
            path = path / 'index'

        with open(path.with_suffix('.json')) as file:
            webpage = WebPage.from_json(json.load(file))

    else:
        error = ("Not found", 404)

    return WebTreeAndPageResponse(root_webtree, webtree, child, webpage, error)


def build_webtree_page(path_str, root_webtree=None):
    if root_webtree is None:
        root_webtree = build_root_webtree()
    webtree = None
    webpage = None
    error = None

    path = Path(path_str)

    abs_url = path_str
    if abs_url:
        abs_url = '/{}/'.format(abs_url)

    child = root_webtree.find_child(abs_url)

    if child is None and path.exists():
        if path.is_dir():
            raw = path_str
        else:
            raw = str(path.parents[0])

        webtree = WebTree.from_dict(raw)
        child = webtree.find_child(abs_url)

    if webtree is None:
        webtree = root_webtree

    parent = child.find_menu(webtree)
    if parent is not None:
        webtree = parent

    if child is not None:
        template = '2col.html'

        if child.use_auto_index and child.is_index_page:
            webpage = child.index_webpage()
            template = 'index.html'
        else:
            webpage, error = generate_html(child.file_path)

        if error is None:
            webpage = webpage.merge_create(root_webtree, webtree, child, template)

    return WebTreeAndPageResponse(root_webtree, webtree, child, webpage, error)


def generate_html(path):
    mdfile = Path(path)

    if not mdfile.exists():
        mdfile = Path(path + ".md")

    if mdfile.is_dir():
        mdfile = mdfile / "index.md"

    # print("Md file", mdfile)

    if (not mdfile.exists()):
        return None, ("Not found", 404)

    md = get_md_class()
    content = md.convert(mdfile.read_text())
    meta = md.Meta
    page = WebPage.from_meta(meta, content)
    md.reset()
    return page, None


def generate(src, output, media=None):
    src_path = Path(src)
    out_path = Path(output)

    if media is None:
        media_path = out_path / 'static'
    else:
        media_path = Path(media)

    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        'markdown.extensions.fenced_code',
        'markdown.extensions.attr_list',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        ])
    for md_file in src_path.glob("**/*.md"):
        rel_parent = md_file.relative_to(src_path).parent
        out_dir = out_path / rel_parent
        if not out_dir.exists():
            print('Creating new DIR', out_dir)
            out_dir.mkdir(parents=True)

        out_file = out_dir / (md_file.name[:-3] + ".html")
        print('Creating', out_file)
        html = md.convert(md_file.read_text())
        out_file.write_text(html)
        md.reset()

    print('Coping snippets')
    snippet_folder = out_path / '_snippets'
    if snippet_folder.exists():
        shutil.rmtree(snippet_folder)
    shutil.copytree(src_path / '_snippets/', snippet_folder)

    print('Coping media files')
    if media_path.exists():
        shutil.rmtree(media_path)
    shutil.copytree(src_path / 'static/', media_path)
