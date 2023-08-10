from CLUSTER_fat32 import Cluster_Array
from DIRECTORY_fat32 import File, Directory
from FAT_fat32 import FAT_Table, FAT_Table_Entry


class Virtual_FS:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _data_size: int, _cluster_size: int):
        self.data_size = _data_size
        self.cluster_size = _cluster_size
        self.fat_table_count = int(self.data_size / self.cluster_size)

        self.fat_table = FAT_Table(self.fat_table_count)
        self.cluster_array = Cluster_Array(self.fat_table_count)

        # self.fat_table.add_entry(0, FAT_Table_Entry(0))

    def serialize(self) -> bytes:
        # print(len(self.fat_table.serialize()))
        # print(len(self.cluster_array.serialize()))
        return self.fat_table.serialize() + self.cluster_array.serialize()

    def write_by_addr(self, _addr: int, data: bytes):

        if self.fat_table.get_next(_addr) == -1:
            self.fat_table.add_entry(_addr, FAT_Table_Entry(0))

        self.cluster_array.clear_cluster(_addr)
        self.cluster_array.write_to_index(_addr, data)
        if len(data) > 4 * 1024:
            self.fat_table.append_to_cluster(_addr)
            self.write_by_addr(self.fat_table.get_next(_addr), data[4096:])

    def read_by_addr(self, _addr: int) -> bytes:
        result = b''
        result = bytes(result) + bytes(self.cluster_array.get_cluster_by_addr(_addr).serialize())
        if self.fat_table.get_next(_addr) > 0:
            result = bytes(result) + bytes(self.read_by_addr(self.fat_table.get_next(_addr)))
        return result

    def write_object(self, _file: File | Directory):
        self.write_by_addr(_file.cluster, _file.serialize())

    def deserialize(self, _fat_table_data: bytes, _cluster_array_data: bytes):

        # clear all data
        self.fat_table = FAT_Table(self.fat_table_count)
        self.cluster_array = Cluster_Array(self.fat_table_count)

        # get data from file
        self.fat_table.deserialize(_fat_table_data)
        self.cluster_array.deserialize(_cluster_array_data)

    def get_dir_by_addr(self, _addr: int) -> Directory:
        data = self.read_by_addr(_addr)
        result = Directory.deserialize(data, self)
        result.cluster = _addr
        return result
