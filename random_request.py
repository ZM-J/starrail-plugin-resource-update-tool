import os
import requests
import time
from copy import deepcopy
from PIL import Image
from io import BytesIO
import shutil


WORKDIR = 'images'
MIAO_YUNZAI_DIR = 'D:\\code\\Miao-Yunzai'
MIAO_PLUGIN_DIR = os.path.join(MIAO_YUNZAI_DIR, 'plugins', 'miao-plugin')
STARRAIL_PLUGIN_DIR = os.path.join(MIAO_YUNZAI_DIR, 'plugins', 'StarRail-plugin')

class Panel:
    def __init__(self, uid):
        self.uid = uid
        self._get_panel_json()

    def _get_panel_json(self):
        url = f'https://avocado.wiki/v1/info/{self.uid}?lang=cn'
        while True:
            res = requests.get(url)
            self._panel_json = res.json()
            if 'msg' in self._panel_json:
                time.sleep(0.5)
            else:
                break
    
    def get_character(self, character_name: str):
        detail_info = self._panel_json['playerDetailInfo']
        if not detail_info['isDisplayAvatarList']:
            return None
        character_list = deepcopy(detail_info['displayAvatars'])
        character_list.append(detail_info['assistAvatar'])
        for character in character_list:
            if character['name'] == character_name:
                return character

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

    def update_starrail_resource(self):
        image2to_folder = {
            'icon': 'resources/gatcha/images/char',
            # '': 'resources/gachasimulation/resources/images/char_image'
            'mini_icon': 'resources/panel/resources/avatar',
            'art': 'resources/panel/resources/char_image',
        }
        for image_name, to_folder in zip(image2to_folder):
            from_image_name = os.path.join(self.character_save_dir, f'{image_name}.png')
            to_image_name = os.path.join(STARRAIL_PLUGIN_DIR, to_folder, f'{self.avatar_id}.png')
            shutil.copy(from_image_name, to_image_name)

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
            print(f'{output_path = }')
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
        behavior_names = [
            'basic_atk',
            'skill',
            'ultimate1',
            'talent',
            'technique',
            'skilltree1',
            'skilltree2',
            'skilltree3',
        ]
        for behavior, benavior_name in zip(self._info['behaviorList'], behavior_names):
            behavior_url = behavior['icon']
            self._download_one_character_image(benavior_name, behavior_url, self.behavior_save_dir)

def test_get_json():
    uid = 100248929
    panel = Panel(uid)
    character = panel.get_character('刃') # 波提欧
    if character is None:
        return
    character = Character()
    character.download_images()

if __name__ == '__main__':
    test_get_json()