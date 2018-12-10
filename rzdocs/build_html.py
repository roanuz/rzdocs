import json
import os
import re
import shutil
from pathlib import Path
from dataclasses import dataclass
from .build import build_root_webtree, build_webtree_page


@dataclass
class HtmlBuildConfig:
    name: str
    full_url: str = ''

    base_url: str = None
    media_url: str = None

    dist_folder: str = 'build/json'
    src_folder: str = ''

    copy_media: bool = True
    dist_media_folder: str = None

    @classmethod
    def from_json(cls, raw):
        config = HtmlBuildConfig(raw['name'])

        config.full_url = raw.get('full_url', config.full_url)
        config.base_url = raw.get('base_url', config.base_url)
        config.media_url = raw.get('media_url', config.media_url)

        config.dist_folder = raw.get('dist_folder', config.dist_folder)
        config.src_folder = raw.get('src_folder', config.src_folder)

        config.copy_media = raw.get('copy_media', config.copy_media)
        config.dist_media_folder = raw.get('dist_media_folder', config.dist_media_folder)

        return config


def load_config(config_file=None):
    configs = []
    if config_file is None:
        config_file = 'build.json'

    if Path(config_file).exists():
        with open(config_file) as jsonfile:
            configs_json = json.load(jsonfile)
            for raw in configs_json['builds']:
                configs.append(HtmlBuildConfig.from_json(raw))
    else:
        configs = [HtmlBuildConfig('default')]

    return configs


def run_build(config_file=None):
    configs = load_config(config_file)

    for config in configs:
        run_build_config(config)


def run_build_config(config):
    dist_folder = Path(config.dist_folder)
    print('Running {} -> {}'.format(config.name, dist_folder))
    if not dist_folder.exists():
        dist_folder.mkdir(parents=True)

    dist_folder = dist_folder.resolve()
    config.dist_folder = dist_folder

    src_folder = Path(config.src_folder).resolve()
    os.chdir(src_folder)
    root_tree = build_root_webtree()
    build_page(config, '', root_tree)

    json_path = dist_folder / '_tree.json'

    with open(json_path, 'w') as file:
        print('Writing Tree', json_path)
        json.dump(root_tree.to_dict(), file)

    dist_media_folder = config.dist_media_folder
    if dist_media_folder is None:
        dist_media_folder = 'media'

    dist_media_folder = dist_folder / dist_media_folder
    src_media_path = src_folder / 'media'
    print('Copying Media to {}'.format(src_media_path))
    if dist_media_folder.exists():
        shutil.rmtree(dist_media_folder)
    shutil.copytree(src_media_path, dist_media_folder)
    print('Done!')


def build_page(config, path, root_tree):
    tree_page = build_webtree_page(path, root_tree)
    page_json = tree_page.webpage.to_dict()
    content = page_json['content']

    if config.media_url:
        content = re.sub(r'src=\"\/media/', 'src="' + config.media_url, content)
        content = re.sub(r'href=\"\/media/', 'href="' + config.media_url, content)

    if config.base_url:
        content = re.sub(r'href=\"\/', 'href="' + config.base_url, content)

    json_path = Path(config.dist_folder) / tree_page.child.abs_url[1:]

    if tree_page.child.is_index_page:
        if not json_path.exists():
            json_path.mkdir()

        if tree_page.child.use_auto_index:
            json_path = json_path / 'index'

    json_path = json_path.with_suffix('.json')

    with open(json_path, 'w') as file:
        print('Writing', json_path)
        json.dump(page_json, file)

    for child in tree_page.child.children:
        build_page(config, child.abs_url[1:-1], root_tree)
