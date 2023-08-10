import struct
from typing import List


class DE_Table_Entry:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _filename: str, _extension: str, _cluster: int, _attributes: int):
        if len(_filename) > 18:
            raise ValueError("Filename cant be longer 18 characters")
        if len(_extension) > 6:
            raise ValueError("File extension cant be longer 6 characters")
        self.filename = _filename
        self.extension = _extension
        self.attributes = _attributes
        self.cluster = _cluster

    def serialize(self) -> bytes:
        return struct.pack(f"18s6sii",
                           self.filename.encode('utf-8'),
                           self.extension.encode('utf-8'),
                           self.cluster,
                           self.attributes)

    def deserialize(self, data: bytes):
        if len(data) != 32:
            raise Exception("length of Directory entry must be 32 bytes")

        result = struct.unpack(f"18s6sii", data)
        self.filename = result[0].rstrip(b'\x00').decode('utf-8')
        self.extension = result[1].rstrip(b'\x00').decode('utf-8')
        self.cluster = result[2]
        self.attributes = result[3]


FAT_EMPTY_ATTRIBUTE = 0
FAT_IS_DIRECTORY_ATTRIBUTE = (1 << 0)
FAT_IS_FILE_ATTRIBUTE = (1 << 1)

