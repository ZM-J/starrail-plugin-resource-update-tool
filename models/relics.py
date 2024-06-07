import os
import shutil
import requests
import json
import yaml
from PIL import Image
from io import BytesIO
from cn_sort.process_cn_word import *

from config import *
from models.base_model import BaseModel


class Relics(BaseModel):
    _all_info = json.load(open(os.path.join(MIAO_PLUGIN_DIR,
                                            'resources/meta-sr/artifact/data.json'),
                               'r',
                               encoding='utf-8'))
    def __init__(self, info) -> None:
        self._info = info
        self.name = self._info['name']
        self.id = self._info['id']

    @classmethod
    def from_miao_plugin(cls, set_name: str):
        for k, v in Relics._all_info.items():
            if v.get('name') == set_name:
                return Relics(v)

    def update_starrail_plugin_resource(self):
        self._update_relics_resource()
        self._update_relics_json()
    
    def _update_relics_resource(self):
        from_image_folder = os.path.join(MIAO_PLUGIN_DIR,
                                         f'resources/meta-sr/artifact/{self.name}')
        to_image_folder = os.path.join(STARRAIL_PLUGIN_DIR,
                                       f'resources/panel/resources/relic')
        from2tofilename = {f'arti-0.webp': f'{self.id}.png'}
        for part_k, v in self._info['idxs'].items():
            from2tofilename[f'arti-{part_k}.webp'] = self._get_icon(part_k)
        for from_image_filename, to_image_filename in from2tofilename.items():
            from_image_name = os.path.join(from_image_folder, from_image_filename)
            to_image_name = os.path.join(to_image_folder, to_image_filename)
            self._convert_webp_to_png(from_image_name,
                                      to_image_name)
    
    def _get_type(self, part_k):
        return {
            "1": "HEAD",
            "2": "HAND",
            "3": "BODY",
            "4": "FOOT",
            "5": "NECK",
            "6": "OBJECT"
        }[part_k]

    def _get_max_level(self, level_v):
        return 3 * level_v

    def _get_main_affix_id(self, level_v, part_k):
        return f'{level_v}{part_k}'

    def _get_sub_affix_id(self, level_v):
        return f'{level_v}'

    def _get_icon(self, part_k):
        if self.id[0] == '1':
            # 外圈
            return f'{self.id}_{int(part_k)-1}.png'
        else:
            # 内圈
            return f'{self.id}_{int(part_k)-5}.png'

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

    def _update_relics_json(self):
        json_path = os.path.join(STARRAIL_PLUGIN_DIR, 'resources/panel/data/relics.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            relics_info = json.load(f)

        for part_k, part_v in self._info['idxs'].items():
            for level_k, level_v in part_v['ids'].items():
                relics_info.update({
                    level_k: {
                        "id": level_k,
                        "set_id": self.id,
                        "name": part_v['name'],
                        "rarity": level_v,
                        "type": self._get_type(part_k),
                        "max_level": self._get_max_level(level_v),
                        "main_affix_id": self._get_main_affix_id(level_v, part_k),
                        "sub_affix_id": self._get_sub_affix_id(level_v),
                        "icon": self._get_icon(part_k)
                    },
                })
        
        # A trick to keep the order of avatar_id
        sequence_relics_info = {}
        relics_key_list = sorted(relics_info.keys())
        for k in relics_key_list:
            sequence_relics_info[k] = relics_info[k]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sequence_relics_info, f, indent=2, ensure_ascii=False)
