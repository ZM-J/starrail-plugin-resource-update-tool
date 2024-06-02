import os
import shutil
import requests
import json
import yaml
from PIL import Image
from io import BytesIO
from cn_sort.process_cn_word import *

from config import *


class Character:
    def __init__(self, info) -> None:
        self._info = info
        self.name = self._info['name']
        self.avatar_id = self._info['avatarId']
        self.image_save_dir = os.path.join(WORKDIR, f'{self.name}')
        self._create_folder(self.image_save_dir)
        self.character_save_dir = os.path.join(self.image_save_dir, 'character')
        self._create_folder(self.character_save_dir)
        self.behavior_save_dir = os.path.join(self.image_save_dir, 'behavior')
        self._create_folder(self.behavior_save_dir)

        self._behavior_names = [
            'basic_atk',
            'skill',
            'ultimate1',
            'talent',
            'technique',
            'skilltree1',
            'skilltree2',
            'skilltree3',
        ]

    def update_starrail_plugin_resource(self):
        self._update_character_resource()
        self._update_behavior_resource()
        self._borrow_from_miao_plugin()
        self._update_character_json()
        self._update_alias()

    def _borrow_from_miao_plugin(self):
        miao2sr = {
            f'resources/meta-sr/character/{self.name}/imgs/cons-1.webp': f'resources/panel/resources/skill/{self.avatar_id}_rank1.png',
            f'resources/meta-sr/character/{self.name}/imgs/cons-2.webp': f'resources/panel/resources/skill/{self.avatar_id}_rank2.png',
            f'resources/meta-sr/character/{self.name}/imgs/cons-4.webp': f'resources/panel/resources/skill/{self.avatar_id}_rank4.png',
            f'resources/meta-sr/character/{self.name}/imgs/cons-6.webp': f'resources/panel/resources/skill/{self.avatar_id}_rank6.png',
            f'resources/meta-sr/character/{self.name}/imgs/talent-q.webp': f'resources/panel/resources/skill/{self.avatar_id}_ultimate.png',
            f'resources/meta-sr/character/{self.name}/imgs/face.webp': f'resources/gatcha/images/char/{self.avatar_id}.png',
        }
        for miao_image_name, sr_image_name in miao2sr.items():
            from_image_name = os.path.join(MIAO_PLUGIN_DIR, miao_image_name)
            to_image_name = os.path.join(STARRAIL_PLUGIN_DIR, sr_image_name)
            self._convert_webp_to_png(from_image_name, to_image_name)
    
    def _update_character_resource(self):
        image2to_folder = {
            # 'icon': 'resources/gatcha/images/char',
            # '': 'resources/gachasimulation/resources/images/char_image'
            'mini_icon': 'resources/panel/resources/avatar',
            'art': 'resources/panel/resources/char_image',
        }
        for image_name, to_folder in image2to_folder.items():
            from_image_name = os.path.join(self.character_save_dir, f'{image_name}.png')
            to_image_name = os.path.join(STARRAIL_PLUGIN_DIR, to_folder, f'{self.avatar_id}.png')
            shutil.copy(from_image_name, to_image_name)

    def _update_behavior_resource(self):
        skill_folder = os.path.join(STARRAIL_PLUGIN_DIR, 'resources/panel/resources/skill')
        for behavior_name in self._behavior_names:
            from_image_name = os.path.join(self.behavior_save_dir, f'{behavior_name}.png')
            to_image_name = os.path.join(skill_folder, f'{self.avatar_id}_{behavior_name}.png')
            shutil.copy(from_image_name, to_image_name)
    
    def _update_alias(self):
        yaml_path = os.path.join(STARRAIL_PLUGIN_DIR, 'defSet/alias.yaml')
        with open(yaml_path, 'r', encoding='utf-8') as f:
            alias = yaml.full_load(f)
        
        # Update English name (inaccurately)
        alias[self.name] = [self._info['vo_tag'][0].upper() + self._info['vo_tag'][1:]]

        # A trick to keep the order of avatar_id
        sequence_alias = {}
        alias_key_list = sort_text_list(alias.keys(), mode=Mode.PINYIN)
        for k in alias_key_list:
            sequence_alias[k] = alias[k]
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(sequence_alias, f, indent=4, allow_unicode=True, sort_keys=False)
    
    def _get_rarity(self):
        return int(self._info['rarity'][-1])

    def _get_path(self):
        # 假设没有 SB 穿不同命途的光锥
        return self._info['equipment']['basic_desc'][:2]

    def _get_element(self):
        return {
            'Wind': '风',
            'Imaginary': '虚数',
            'Physical': '物理',
            'Quantum': '量子',
            'Lightning': '雷',
            'Fire': '火',
            'Ice': '冰',
        }[self._info['damage_type']]

    def _update_character_json(self):
        json_path = os.path.join(STARRAIL_PLUGIN_DIR, 'resources/panel/data/character.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            character_info = json.load(f)
        if str(self.avatar_id) not in character_info:
            character_info[str(self.avatar_id)] = {
                'id': str(self.avatar_id),
                'name': self.name,
                'tag': self._info['vo_tag'],
                'rarity': self._get_rarity(),
                'path': self._get_path(),
                'element': self._get_element(),
            }
        
        # A trick to keep the order of avatar_id
        sequence_character_info = {}
        character_key_list = sorted(character_info.keys())
        for k in character_key_list:
            sequence_character_info[k] = character_info[k]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sequence_character_info, f, indent=2, ensure_ascii=False)
            f.write('\n')

    def download_images(self):
        self._download_character_images()
        self._download_behavior_images()

    def _create_folder(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)

    def _convert_webp_to_png(self, webp_image_data, output_path):
        # 打开 WebP 图片
        with Image.open(webp_image_data) as webp_image:
            # 确保图片有 alpha 通道
            if webp_image.mode != 'RGBA':
                webp_image = webp_image.convert('RGBA')
            # 保存为 PNG
            webp_image.save(output_path, 'PNG')

    def _get_full_url(self, url):
        return f'https://avocado.wiki{url}'

    def _download_one_character_image(self, image_name, url, save_folder):
        response = requests.get(self._get_full_url(url))
        response.raise_for_status()
        webp_image = BytesIO(response.content)
        self._convert_webp_to_png(webp_image,
                                  os.path.join(save_folder, f'{image_name}.png'))

    def _download_character_images(self):
        for image_name, url in self._info['images'].items():
            self._download_one_character_image(image_name, url, self.character_save_dir)
    
    def _download_behavior_images(self):
        for behavior, benavior_name in zip(self._info['behaviorList'], self._behavior_names):
            behavior_url = behavior['icon']
            self._download_one_character_image(benavior_name, behavior_url, self.behavior_save_dir)