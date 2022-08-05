
import os
import pickle
import sys
from src.core.user import User
from typing import List, Tuple


class Storage:
    """数据持久化,需要管理多个User,使用pickle"""
    DATA_FILE = '.1BF52todo'
    # 单例，简化存储的实现
    instance = None
    def __init__(self) -> None:
        self.users: List[User] = []
        self.path = os.path.expanduser('~')  # Users\pc or ~/pc
    @staticmethod
    def get_instance() -> 'Storage':
        return Storage.instance
    @staticmethod
    def try_load() -> Tuple['Storage', bool, bool]:
        """return (object, created, ok)"""
        path = os.path.expanduser('~')
        file_path = os.path.join(path, Storage.DATA_FILE)
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    o = pickle.load(f)
                    print(o.__dict__)
                    if not isinstance(o, Storage):
                        print(f"损坏的资源文件{file_path},(尝试删除以修复)")
                        return None, False, False
                    o.path = os.path.expanduser('~')
                    Storage.instance = o
                    return o, False, True
            except:
                print(sys.exc_info())
                print(f"无法打开资源文件{file_path}")
                return None, False, False
        else:
            Storage.instance = Storage()
            return Storage.instance, True, True

    @staticmethod
    def try_store(s: 'Storage') -> bool:
        path = os.path.expanduser('~')
        file_path = os.path.join(path, Storage.DATA_FILE)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(s, f)
                return True
        except:
            print(f"无法保存资源文件{file_path}")
            return False

    def get_user_by_name(self, name: str) -> User:
        for u in self.users:
            if u.name == name:
                return u
        return None
    
    def get_user_names(self) -> List[str]:
        ret = []
        for u in self.users:
            ret.append(u.name)

        return ret

    @staticmethod
    def save():
        """不能保证用户在何时以何种方式退出应用,所以每次修改都需要保存,
        使用Qt信号实现过于复杂,使用单例"""
        path = os.path.expanduser('~')
        file_path = os.path.join(path, Storage.DATA_FILE)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(Storage.instance, f)
        except:
            with open("err.txt","w+") as f:
                f.write(f"无法保存资源文件{file_path}")
