import struct
from typing import Dict, List, Optional

from DE_fat32 import FAT_IS_DIRECTORY_ATTRIBUTE, FAT_IS_FILE_ATTRIBUTE, DE_Table_Entry


class Directory:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _name: str, _cluster: int):
        if len(_name) > 18:
            raise ValueError("Filename cant be longer 18 characters")
        self.name = _name
        self.extension = ""
        self.attributes = FAT_IS_DIRECTORY_ATTRIBUTE
        self.cluster = _cluster
        self.entries = []

    def get_table_entry(self) -> DE_Table_Entry:
        return DE_Table_Entry(self.name, self.extension, self.cluster, self.attributes)

    def serialize(self):
        result = [0] * (len(self.entries) * 32)
        for index, item in enumerate(self.entries):
            offset = index * 32
            data_start = offset
            data_end = data_start + 32

            result[data_start:data_end] = list(item.get_table_entry().serialize())

        return bytes(result)

    def add_subdirectory(self, _dir: 'Directory'):
        self.entries.append(_dir)

    def add_file(self, _file: 'File'):
        self.entries.append(_file)

    def get_dir_names_list(self) -> List[str]:
        result = []
        for entry in self.entries:
            if entry.attributes == FAT_IS_DIRECTORY_ATTRIBUTE:
                stripped_name = entry.name
                result.append(f"{stripped_name}")
            elif entry.attributes == FAT_IS_FILE_ATTRIBUTE:
                stripped_name = entry.name
                extension_name = entry.extension
                result.append(f"{stripped_name}.{extension_name}")
        return result

    def get_files_list(self) -> List[str]:

        result = []
        for entry in self.entries:
            if entry.attributes == FAT_IS_FILE_ATTRIBUTE:
                stripped_name = entry.name
                stripped_extension = entry.extension

                result.append(f"{stripped_name}.{stripped_extension}")
        return result

    def get_dirs_list(self) -> List['str']:

        result = []
        for entry in self.entries:
            if entry.attributes == FAT_IS_DIRECTORY_ATTRIBUTE:
                stripped_name = entry.name
                result.append(f"{stripped_name}")
        return result

    def get_directory_by_name(self, _name: str) -> Optional['Directory']:
        arr = [entry for entry in self.entries if
               entry.attributes == FAT_IS_DIRECTORY_ATTRIBUTE and entry.name == _name]
        if len(arr) > 1:
            raise Exception("there cant be more than 1 dir with same name")
        if len(arr) == 0:
            return None
        return arr[0]

    def get_path_append(self) -> str:
        return self.name + '/'

    @classmethod
    def deserialize(cls, data: bytes) -> 'Directory':
        count = 0

        result = Directory("", -1)

        for i in range(0, len(data), 32):
            unpacked_data = DE_Table_Entry("", "", -1, 1)
            unpacked_data.deserialize(data[i:i+32])

            if unpacked_data.attributes == FAT_IS_DIRECTORY_ATTRIBUTE:
                result.add_subdirectory(Directory(unpacked_data.filename, unpacked_data.cluster))
            elif unpacked_data.attributes == FAT_IS_FILE_ATTRIBUTE:
                result.add_file(
                    File(unpacked_data.filename, unpacked_data.extension, unpacked_data.cluster, "".encode('UTF-8')))

            count += 1

        return result


class File:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _name: str, _extension: str, _cluster: int, _content: bytes):
        if len(_name) > 18:
            raise ValueError("Filename cant be longer 18 characters")
        self.name = _name
        self.extension = _extension
        self.attributes = FAT_IS_FILE_ATTRIBUTE
        self.cluster = _cluster
        self.content = _content

    def get_table_entry(self) -> DE_Table_Entry:
        return DE_Table_Entry(self.name, self.extension, self.cluster, self.attributes)

    def serialize(self) -> bytes:
        return self.content


def get_absolute_path(_path: List[Directory]) -> str:
    return ''.join([directory.get_path_append() for directory in _path])
