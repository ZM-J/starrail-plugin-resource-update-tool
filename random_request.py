import random
from models import Panel, Character


def test_get_json():
    uid = 101075816
    panel = Panel(uid)
    character = panel.get_character('知更鸟')
    if character is None:
        print('No character found.')
        return
    else:
        character = Character(character)
        character.download_images()
        character.update_starrail_plugin_resource()
        print('Character updated.')

def test_random_request():
    character_name = '知更鸟'
    while True:
        uid = 100000000 + random.randrange(10000000)
        panel = Panel(uid)
        character = panel.get_character(character_name)
        if character is None:
            print(f'{uid} failed...')
            continue
        else:
            print(f'{uid = }')
            character = Character(character)
            # character.download_images()
            # character.update_starrail_plugin_resource()
            break

if __name__ == '__main__':
    test_get_json()
    # test_random_request()