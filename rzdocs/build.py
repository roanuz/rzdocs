from pathlib import Path
from .page import WebTree, WebPage
import yaml
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


def build_menu(path_str):
    webtree = build_root_webtree()

    path = Path(path_str)

    abs_url = path_str
    if abs_url:
        abs_url = '/{}/'.format(abs_url)

    page = webtree.find_page(abs_url)

    if page is None and path.exists():
        if path.is_dir():
            raw = path_str
        else:
            raw = str(path.parents[0])

        webtree = WebTree.from_dict(raw)
        page = webtree.find_page(abs_url)

    parent = page.find_menu(webtree)
    return webtree if parent is None else parent, page


def generate_html(path):
    mdfile = Path(path)

    if not mdfile.exists():
        mdfile = Path(path + ".md")

    if mdfile.is_dir():
        mdfile = mdfile / "index.md"

    # print("Md file", mdfile)

    if (not mdfile.exists()):
        return "Not found", 404

    md = get_md_class()
    content = md.convert(mdfile.read_text())
    meta = md.Meta
    page = WebPage.from_meta(meta, content)
    md.reset()
    return page


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
