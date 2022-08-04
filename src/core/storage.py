
import os
import pickle
from typing import Tuple


class Storage:
    """数据持久化,需要管理多个User,使用pickle"""
    DATA_FILE = '1BF52todo'

    def __init__(self) -> None:
        self.users = []
        self.path = os.path.expanduser('~')  # Users\pc or ~/pc

    @staticmethod
    def try_load() -> Tuple['Storage', bool, bool]:
        """return (object, created, ok)"""
        path = os.path.expanduser('~')
        file_path = os.path.join(path, Storage.DATA_FILE)
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    o = pickle.load(f)
                    if not isinstance(o, Storage): 
                        print("损坏的资源文件{file_path}")
                        return None, False, False
                    o.path = os.path.expanduser('~')
                    return o, False, True
            except:
                print("无法打开资源文件{file_path}")
                return None, False, False
        else:
            return Storage(), True, True