import os
import requests
from PIL import Image
from io import BytesIO


class BaseModel:
    def __init__(self):
        pass

    def _get_full_url(self, url):
        return f'https://avocado.wiki{url}'

    def _download_one_character_image(self, image_name, url, save_folder):
        response = requests.get(self._get_full_url(url))
        response.raise_for_status()
        webp_image = BytesIO(response.content)
        self._convert_webp_to_png(webp_image,
                                  os.path.join(save_folder, f'{image_name}.png'))
    
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