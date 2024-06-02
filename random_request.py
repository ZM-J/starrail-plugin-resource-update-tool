from models import Panel, Character


def test_get_json():
    uid = 100248929
    panel = Panel(uid)
    character = panel.get_character('刃') # 波提欧
    if character is None:
        return
    character = Character(character)
    character.download_images()

if __name__ == '__main__':
    test_get_json()