# @Author: ericlwc

# date:
# 2023/06/30 撰寫

import os

class Path:
    """
    路徑解析器

    Attributes:
        path: 路徑
        type: 路徑的目標類型，為"file"或"dir"
        is_abs_path: 是否為絕對路徑
        is_rel_path: 是否為相對路徑
        abs_path: 絕對路徑
        rel_path: 相對路徑
        is_dir: 是否為資料夾
        is_file: 是否為檔案
        abs_parent_dir: 所在的資料夾絕對路徑
        rel_parent_dir: 所在的資料夾相對路徑
        name: 檔案全名
        main_name: 主檔名
        extension: 副檔名
        is_existed_file: 是否為已存在的檔案
        is_existed_dir: 是否為已存在的資料夾
        is_existed: 是否為已存在的檔案或資料夾
    
    Methods:
        get_nth_parent_dir(n): 以當前的絕對路徑為基礎，從最父層級的資料夾開始，獲取第n層的資料夾路徑
        get_parent_dir_num(): 獲取當前路徑的父層級資料夾數量
        mkdirs(): 創建資料夾

    Examples:
        >>> path = Path("C:/Users/ericlwc/Desktop/Python/PathParser.py")
        >>> path.abs_path
        'C:/Users/ericlwc/Desktop/Python/PathParser.py'
        >>> path.rel_path
        './PathParser.py'
    """
    def __init__(self, path, type="auto"):
        """
        實例化路徑解析器

        Args:
            path: 路徑
            type: 路徑的目標類型，可選值為"auto", "file", "dir"，預設為"auto"，即自動判斷該路徑是指向檔案還是資料夾
        """
        self.path = path.replace("\\", "/")

        if type == "auto":
            if os.path.isdir(self.path):
                self.type = "dir"
            elif os.path.isfile(self.path):
                self.type = "file"
            else:
                raise ValueError("Can't determine the type of the path is a file or directory, since the path doesn't exist.")
            
        elif type == "file":
            if os.path.isfile(self.path):
                self.type = "file"
            elif os.path.isdir(self.path):
                raise ValueError("The path is already existed, and it is a directory, not a file.")
            else:
                self.type = "file"

        elif type == "dir":
            if os.path.isdir(self.path):
                self.type = "dir"
            elif os.path.isfile(self.path):
                raise ValueError("The path is already existed, and it is a file, not a directory.")
            else:
                self.type = "dir"

        else:
            raise ValueError("Invalid type. It must be 'auto', 'file', or 'dir'.")

    # 輸入的原始路徑是絕對路徑
    @property
    def is_abs_path(self):
        return os.path.isabs(self.path)
    
    # 輸入的原始路徑是相對路徑
    @property
    def is_rel_path(self):
        return not os.path.isabs(self.path)

    # 絕對路徑
    @property
    def abs_path(self):
        return os.path.abspath(self.path)
    
    # 相對路徑
    @property
    def rel_path(self):
        rel_path = os.path.relpath(self.path)
        return rel_path
    
    # 是資料夾
    @property
    def is_dir(self):
        return self.type == "dir"
    
    # 是檔案
    @property
    def is_file(self):
        return self.type == "file"

    # 所在的資料夾絕對路徑
    @property
    def abs_parent_dir(self):
        return os.path.dirname(self.abs_path)
    
    # 所在的資料夾相對路徑
    @property
    def rel_parent_dir(self):
        return os.path.dirname(self.rel_path)
    
    # 檔案全名
    @property
    def name(self):
        return os.path.basename(self.abs_path)
    
    # 主檔名
    @property
    def main_name(self):
        name = os.path.basename(self.abs_path)
        return os.path.splitext(name)[0]
    
    # 副檔名
    @property
    def extension(self):
        """
        extention of the file (LOWER)
        """
        is_dir = self.is_dir
        is_file = self.is_file
        abs_path = self.abs_path
        name = self.name

        if is_dir:
            return f"\033[33mWARNING, '{abs_path}' is directory\033[0m" # yellow warning
        elif is_file:
            return (os.path.splitext(name)[1].replace(".", "")).lower()
    
    # 是已經存在的檔案
    @property
    def is_existed_file(self):
        is_dir = self.is_dir
        is_file = self.is_file
        abs_path = self.abs_path

        if is_dir:
            return False
        elif is_file:
            return os.path.isfile(abs_path)

    # 是已經存在的資料夾
    @property
    def is_existed_dir(self):
        is_dir = self.is_dir
        is_file = self.is_file
        abs_path = self.abs_path
        
        if is_dir:
            return os.path.isdir(abs_path)
        elif is_file:
            return False
        
    # 是否存在
    @property
    def is_existed(self):
        return True if self.is_existed_file or self.is_existed_dir else False
        
    # 獲取第n層的資料夾路徑
    def get_nth_parent_dir(self, n):
        """
        以當前的絕對路徑為基礎，從最父層級的資料夾開始，獲取第n層的資料夾路徑

        Args:
            n: 第n層

        Returns:
            第n層的資料夾絕對路徑
        
        Examples:
            >>> path = Path("C:/Users/test/Desktop/Python/test.txt")
            >>> path.get_nth_parent_dir(n=0)
            'C:/'
            >>> path.get_nth_parent_dir(n=1)
            'C:/Users'
            >>> path.get_nth_parent_dir(n=2)
            'C:/Users/test'
            >>> path.get_nth_parent_dir(n=3)
            'C:/Users/test/Desktop'
            >>> path.get_nth_parent_dir(n=4)
            'C:/Users/test/Desktop/Python'
            >>> path.get_nth_parent_dir(n=5)
            None
        """
        # get absolute path
        path_list = self.abs_path.split("/")

        # if path is file, remove file name
        if self.is_file:
            path_list.pop()

        # return
        if n < len(path_list):
            return "/".join(path_list[:n+1])
        else:
            return None
        
    # 獲得他共有幾層的父資料夾
    def get_parent_dir_num(self):
        """
        獲得有幾層的父資料夾。需注意，檔案的資料夾層數為檔案所在的資料夾層數！

        Returns:
            資料夾層數
        
        Examples:
            >>> path = Path("C:/Users/test/Desktop/Python/test.txt")
            >>> path.get_parent_dir_num()
            5
        """
        path_list = self.abs_path.split("/")
        return len(path_list)-1 # 扣除自己

    # 創建資料夾
    def mkdirs(self):
        """
        創建出該路徑的資料夾（如果是檔案，則創建至檔案所在的資料夾，如果是資料夾，則創建至該資料夾）
        """
        is_dir = self.is_dir
        is_file = self.is_file
        abs_path = self.abs_path
        abs_parent_dir = self.abs_parent_dir
        is_existed = self.is_existed

        if is_dir and not is_existed:
            os.makedirs(abs_path)
        elif is_file and not is_existed:
            os.makedirs(abs_parent_dir)
        