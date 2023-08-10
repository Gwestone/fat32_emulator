import struct


class Cluster:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _id: int):
        self.id = _id
        self.data = b'\x00' * 4 * 1024

    def serialize(self) -> bytes:
        return self.data

    def deserialize(self, _data: bytes):
        self.data = _data


class Cluster_Array:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, _cluster_count: int):
        self.cluster_count = _cluster_count
        self.clusters = []
        for index in range(0, _cluster_count):
            self.clusters.append(Cluster(index))

    def clear_cluster(self, _id: int):
        self.clusters[_id].data = b'\x00' * 4 * 1024

    def write_to_index(self, _id: int, _data: bytes):
        new_data = list(self.clusters[_id].data)
        new_data[0:len(_data)] = _data
        self.clusters[_id].data = new_data

    def serialize(self):
        result = [0] * (self.cluster_count * 4 * 1024)
        for index, item in enumerate(self.clusters):

            offset = index * 4 * 1024
            data_start = offset
            data_end = data_start + 4 * 1024

            result[data_start:data_end] = list(item.serialize())

        return bytes(result)

    def get_cluster_by_addr(self, _id: int) -> Cluster:
        return self.clusters[_id]

    def deserialize(self, _cluster_array_data: bytes):
        count = 0
        for i in range(0, len(_cluster_array_data), 4 * 1024):
            self.clusters[count].deserialize(_cluster_array_data[i:i + 4 * 1024])
            count += 1

