from pathlib import Path
from dataclasses import dataclass, field, asdict
import re
import yaml


@dataclass
class WebTree:
    name: str
    path: str
    url: str
    children: list = field(default_factory=list)
    include_all_children: bool = False

    meta: dict = field(default_factory=dict)
    visible_to: str = 'public'

    file_path: Path = None
    abs_url: str = None
    level: int = 0
    is_link: bool = False
    is_index_page: bool = False
    use_auto_index: bool = False
    use_as_menu: bool = False
    parent_abs_url: str = None
    template: str = None
    default_template: str = None

    def print_tree(self):
        print('{} {} ({}) < {}'.format(' ' * self.level, self.name, self.abs_url, self.use_as_menu))
        for child in self.children:
            child.print_tree()

    def to_dict(self):
        res = asdict(self)
        res['file_path'] = str(self.file_path)
        res['children'] = [c.to_dict() for c in self.children]
        return res


    def index_webpage(self):
        return WebPage(title=None, desc=None, content='', visible_to=None)

    def find_child(self, abs_url):
        if not abs_url:
            abs_url = '/'

        if self.abs_url == abs_url:
            return self
        else:
            for child in self.children:
                page = child.find_child(abs_url)
                if page is not None:
                    return page

        return None

    def find_menu(self, root_webtree):
        if self.use_as_menu:
            return self
        if self.parent_abs_url:
            parent = root_webtree.find_child(self.parent_abs_url)
            if parent is None or parent.use_as_menu:
                return parent
            else:
                return parent.find_menu(root_webtree)

        return None

    def update_is_link(self):
        url = self.url
        if url.startswith('//') or url.startswith('https:') or url.startswith('http:'):
            self.is_link = True

    def update_file_path(self, parent=None):
        path = self.path
        file_path = Path(path)
        if (not path.startswith('/')) and (parent is not None):
            parent_path = parent.file_path
            if not parent_path.is_dir():
                parent_path = parent_path.parent

            file_path = parent_path / path

        if not file_path.exists():
            file_path = file_path.with_suffix('.md')

        if file_path.is_dir():
            self.is_index_page = True
            if (file_path / "index.md").exists():
                file_path = file_path / "index.md"
            else:
                self.use_auto_index = True

        self.file_path = file_path

    def update_abs_url(self, parent=None):
        url = self.url
        if (not url.startswith('/')):
            if (parent is not None):
                url = parent.abs_url + url
            else:
                url = '/' + url

        if not url.endswith('/'):
            url = url + '/'

        self.abs_url = url

    # def inheritable_params(self):
    #     return {
    #         'include-all-children': True
    #     }

    def update_children(self, children, parent):
        abs_urls = []

        for treeraw in children:
            child = WebTree.from_dict(treeraw, self)
            abs_urls.append(child.abs_url)
            self.children.append(child)

        if self.include_all_children and next(self.file_path.glob('**/*.md'), None) is not None:
            new_children = []
            for child in self.file_path.iterdir():
                last_part = child.parts[-1]
                if last_part.startswith('_') or last_part.startswith('.'):
                    continue

                rel_path = child.relative_to(self.file_path)
                if child.is_dir() and next(child.glob('**/*.md'), None) is not None:
                    child_tree = WebTree.from_dict(str(rel_path), self)
                elif child.is_file() and child.suffix == '.md':
                    child_tree = WebTree.from_dict(str(rel_path)[:-3], self)
                else:
                    child_tree = None

                if child_tree and (child_tree.abs_url not in abs_urls):
                    abs_urls.append(child_tree.abs_url)
                    new_children.append(child_tree)

            new_children.sort(key=lambda x: x.abs_url)
            self.children.extend(new_children)

    @classmethod
    def from_json(cls, raw):
        updated_raw = dict()
        updated_raw.update(raw)
        children = raw['children']

        updated_raw['file_path'] = Path(raw['file_path'])
        updated_raw['children'] = []

        tree = WebTree(**updated_raw)
        for child_raw in children:
            child = WebTree.from_json(child_raw)
            tree.children.append(child)

        return tree

    @classmethod
    def from_dict(cls, raw, parent=None, use_as_menu=None):
        if isinstance(raw, str):
            path = raw
            abs_path = Path(path)
            new_raw = None
            if parent is not None:
                parent_path = parent.file_path
                if parent.is_index_page:
                    parent_path = parent.file_path.parent
                abs_path = parent_path / abs_path

            if (abs_path / 'webtree.yaml').exists():
                yfile = (abs_path / 'webtree.yaml')
                with yfile.open() as fs:
                    new_raw = yaml.load(fs)
                    use_as_menu = True

            if new_raw is not None:
                if new_raw.get('path') is None:
                    new_raw['path'] = path
                raw = new_raw
            else:
                raw = dict(path=raw)

        path = raw.get('path', '')
        name = raw.get('name', None)
        url = raw.get('url', path)

        if name is None:
            name = path.split('/')[-1][:]
            if re.match(r'^\d{8}', name):
                name = name[8:]

            name = name.strip().replace('-', ' ').strip()  # .capitalize()

        page = WebTree(path=path, name=name, url=url)
        page.update_is_link()
        page.meta = raw.get('meta', page.meta)
        page.template = raw.get('template', page.template)
        page.default_template = raw.get('default-template', page.default_template)

        include_all_children = raw.get('include-all-children', None)
        visible_to = raw.get('visible-to', None)

        page.visible_to = visible_to
        page.include_all_children = include_all_children

        if use_as_menu is not None:
            page.use_as_menu = use_as_menu

        if parent is not None:
            page.parent_abs_url = parent.abs_url
            page.level = parent.level + 1

            if visible_to is None:
                page.visible_to = parent.visible_to

            if include_all_children is None:
                page.include_all_children = parent.include_all_children

        if page.is_link:
            page.abs_url = page.url
        else:
            page.update_file_path(parent)
            page.update_abs_url(parent)

        page.update_children(raw.get('children', []), parent)
        return page


@dataclass
class WebPage:
    title: str
    desc: str
    content: str = None
    visible_to: str = None
    updated_date: str = None
    template: str = None

    def merge_create(self, root_webtree, webtree, child, template=None):
        if template is None:
            template = 'index.html'

        desc = self.desc
        if desc is None and child.meta:
            desc = child.meta.get('desc', None)

        title = child.name if self.title is None else self.title
        visible_to = child.visible_to if self.visible_to is None else self.visible_to

        if self.template:
            template = self.template
        elif child.template:
            template = child.template
        elif webtree.default_template and (not child.is_index_page):
            template = webtree.default_template

        if not template.endswith('.html'):
            template = template + '.html'

        webpage = WebPage(
            title=title, desc=desc, content=self.content,
            visible_to=visible_to, updated_date=self.updated_date,
            template=template)

        return webpage

    @classmethod
    def from_meta(cls, raw, content=None):
        title = raw.get('title', [None])[0]
        desc = raw.get('desc', [None])[0]
        visible_to = raw.get('visible-to', [None])[0]
        updated_date = raw.get('updated-date', [None])[0]
        template = raw.get('template', [None])[0]

        return WebPage(
            title=title, desc=desc, content=content,
            visible_to=visible_to, updated_date=updated_date,
            template=template)

    @classmethod
    def from_json(cls, raw):
        return WebPage(**raw)

    def to_dict(self):
        return asdict(self)

@dataclass
class WebTreeAndPageResponse:
    root: WebTree
    tree: WebTree
    child: WebTree
    webpage: WebPage
    error: tuple = field(default_factory=tuple)
