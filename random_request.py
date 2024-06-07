import random
from models import Panel, Character, LightCone, Relics


def test_update_character():
    uid = 101234567
    character_name = '波提欧'
    panel = Panel(uid)
    character = panel.get_character(character_name)
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

def test_update_light_cone():
    light_cones = [
        ('同谐', '为了明日的旅途'),
        ('虚无', '无边曼舞')
    ]
    for light_cone_type, light_cone_name in light_cones:
        light_cone = LightCone.from_miao_plugin(light_cone_type, light_cone_name)
        light_cone.update_starrail_plugin_resource()

def test_update_relics():
    set_name = '戍卫风雪的铁卫'
    relics = Relics.from_miao_plugin(set_name)
    relics.update_starrail_plugin_resource()

if __name__ == '__main__':
    # test_update_character()
    # test_random_request()
    # test_update_light_cone()
    test_update_relics()