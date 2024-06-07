import time
import requests
from copy import deepcopy


class Panel:
    def __init__(self, uid):
        self.uid = uid
        self._get_panel_json()

    def _get_panel_json(self):
        url = f'https://avocado.wiki/v1/info/{self.uid}?lang=cn'
        while True:
            res = requests.get(url)
            try:
                self._panel_json = res.json()
            except requests.exceptions.JSONDecodeError:
                time.sleep(0.5)
                continue
            if 'msg' in self._panel_json:
                time.sleep(0.5)
            else:
                break
    
    def _get_all_characters(self):
        detail_info = self._panel_json['playerDetailInfo']
        if not detail_info['isDisplayAvatarList']:
            return None
        character_list = deepcopy(detail_info['displayAvatars'])
        character_list.append(detail_info['assistAvatar'])
        return character_list

    def get_character(self, character_name: str):
        character_list = self._get_all_characters()
        if character_list:
            for character in character_list:
                if character['name'] == character_name:
                    return character
    
    def get_light_cone(self, light_cone_name: str):
        character_list = self._get_all_characters()
        for character in character_list:
            light_cone = character['equipment']
            if light_cone['name'] == light_cone_name:
                return light_cone