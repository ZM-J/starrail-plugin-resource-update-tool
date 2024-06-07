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


class LightCone(BaseModel):
    def __init__(self, info) -> None:
        self._info = info
        self.name = self._info['name']
        self.id = self._info['id']
        self.type = self._info['type']

    @classmethod
    def from_miao_plugin(cls, type: str, name: str):
        miao_plugin_data_path = os.path.join(MIAO_PLUGIN_DIR,
                                             f'resources/meta-sr/weapon/{type}/{name}/data.json')
        with open(miao_plugin_data_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        return LightCone(info)

    def update_starrail_plugin_resource(self):
        self._update_light_cone_resource()
    
    def _update_light_cone_resource(self):
        from_image_name = os.path.join(MIAO_PLUGIN_DIR,
                                       f'resources/meta-sr/weapon/{self.type}/{self.name}/icon-s.webp')
        to_image_name = os.path.join(STARRAIL_PLUGIN_DIR,
                                     f'resources/panel/resources/weapon/{self.id}.png')
        self._convert_webp_to_png(from_image_name,
                                  to_image_name)
