import json
from pathlib import Path


class Config:
    """ 配置类 """

    def __init__(self):
        self.__config = {
            'download-folder': str(Path('download').absolute()).replace("\\", '/'),
            'block-num': 32,
            'auto-restart-speed-percent': 0.5,
            'auto-restart-speed-kilobytes': 88,
            'skin': "Default"
        }
        self.__readConfig()

    def __readConfig(self):
        """ 读入配置文件数据 """
        try:
            with open("config.json", encoding="utf-8") as f:
                self.__config.update(json.load(f))
        except Exception as err:
            print(f"读取配置文件出错{err}")

    def __setitem__(self, key, value):
        if key not in self.__config:
            raise KeyError(f'配置项 `{key}` 非法')

        if self.__config[key] == value:
            return

        self.__config[key] = value
        self.save()

    def __getitem__(self, key):
        return self.__config[key]

    def update(self, config: dict):
        """ 更新配置 """
        for k, v in config.items():
            self[k] = v

    def save(self):
        """ 保存配置 """
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.__config, f)
