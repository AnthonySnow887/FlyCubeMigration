import os
import json
from src.Helper.Helper import Helper


class Settings:
    __name = ""
    __args = {}

    def __init__(self, name: str):
        self.__name = name.strip()
        if self.__name == "":
            return
        dir_path = f"/home/{Helper.current_user()}/.config/{name.capitalize()}"
        file_path = f"{dir_path}/{name.capitalize()}.json"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        if not os.path.exists(file_path):
            return
        with open(file_path, "r") as stream:
            try:
                self.__args = json.load(stream)
            except ValueError as exc:
                return

    def __del__(self):
        self.save_settings()

    def name(self) -> str:
        return self.__name

    def all_keys(self) -> list:
        return list(self.__args.keys())

    def remove_key(self, key: str):
        if key in self.__args:
            del self.__args[key]

    def value(self, key: str, default):
        if not key in self.__args:
            return default
        return self.__args[key]

    def set_value(self, key: str, value):
        self.__args[key] = value

    def save_settings(self):
        if self.__name == "":
            return
        dir_path = f"/home/{Helper.current_user()}/.config/{self.__name.capitalize()}"
        file_path = f"{dir_path}/{self.__name.capitalize()}.json"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        with open(file_path, 'w') as f:
            json.dump(self.__args, f)
