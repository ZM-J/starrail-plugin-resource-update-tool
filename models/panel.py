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