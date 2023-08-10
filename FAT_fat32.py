import struct


class FAT_Table_Entry:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _next_link: int):
        self.next_link = _next_link

    @classmethod
    def deserialize(cls, data: bytes) -> 'FAT_Table_Entry':
        result = FAT_Table_Entry(-1)
        if len(data) != 4:
            raise Exception("Wrong window size")
        result.next_link = struct.unpack('i', data)[0]
        # result.next_link = int.from_bytes(data, byteorder='big')

        return result


class FAT_Table:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, fat_table_entries_count: int):
        self.entries = [FAT_Table_Entry(-1)] * int(fat_table_entries_count)
        self.table_entries_count = fat_table_entries_count

    def add_entry(self, _id: int, _entry: FAT_Table_Entry):
        self.entries[_id] = _entry

    def append_to_cluster(self, _source: int):
        if self.entries[_source].next_link > 0:
            raise Exception("Cant link from already linked file")

        first_index = self.get_next_cluster_index()
        self.entries[_source].next_link = first_index
        self.add_entry(first_index, FAT_Table_Entry(0))

    def get_next_cluster_index(self) -> int:
        return next((index for index, entry in enumerate(self.entries) if entry.next_link == -1), None)

    def serialize(self) -> bytes:
        result = [0] * (self.table_entries_count * 4)
        for index, item in enumerate(self.entries):
            offset = index * 4
            data_start = offset
            data_end = data_start + 4

            result[data_start:data_end] = list(struct.pack('i', item.next_link))

        return bytes(result)

    def print(self):
        for index, item in enumerate(self.entries):
            print(item.next_link)

    def get_next(self, _addr: int) -> int:
        return self.entries[_addr].next_link

    def deserialize(self, _fat_table_data: bytes):
        count = 0
        for i in range(0, len(_fat_table_data), 4):
            # print(_fat_table_data[i:i + 4])
            self.entries[count] = FAT_Table_Entry.deserialize(_fat_table_data[i:i + 4])
            count += 1
