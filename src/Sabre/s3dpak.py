import struct
from PyQt5.QtCore import QFileInfo

class s3dpak():          

    s3d_type_definitions = {
    0 : "Scene Data",
    1 : "Data",
    2 : "Single Player Lines",
    3 : "Shader (.fx, .psh, .vsh)",
    5 : "Textures Info",
    8 : "Sound Data",
    10 : "Memory",
    11 : "Skull data?",
    12 : "Template",
    14 : "String List",
    16 : "Game Logic (.lg)",
    17 : "Breakable glass",
    18 : "effects (.gfx)",
    22 : "(.grs)",
    25 : "rain",
    26 : "(.cdt)",
    27 : "(.sm)",
    29 : "(.vis)"
    }

    class block():
        def __init__(self):
            self.type = 0
            self.offset = 0
            self.size = 0
            self.length_of_string = 0
            self.string = ""

            self.data = None

        def get_data(self, file_stream):
            starting_pos = file_stream.tell()
            file_stream.seek(self.offset)
            self.data = file_stream.read(self.size)
            file_stream.seek(starting_pos)
            return

        def extract(self, location):
            with open(location + "/" + self.string, "wb") as file:
                file.write(self.data)

        def import_block(self, file_location, file_type):
            file_info = QFileInfo(file_location)
            with open(file_location, "rb") as file:
                self.data = file.read()

            for key, value in s3dpak.s3d_type_definitions.items():
                if file_type == value: self.type = key

            self.size = len(self.data)
            self.string = file_info.fileName()
            self.length_of_string = len(file_info.fileName()) if self.string != "SceneData" else 0
            self.offset = 0
            return self

    def __init__(self, file_stream = None):
        self.blocks = {}
        if file_stream == None:return
        block_buffer = self.block()
        file_count = int.from_bytes(file_stream.read(4), "little")

        while file_count > 0:
            block_buffer = self.block()
            block_buffer.offset = int.from_bytes(file_stream.read(4), "little")
            block_buffer.size = int.from_bytes(file_stream.read(4), "little")
            block_buffer.length_of_string = int.from_bytes(file_stream.read(4), "little")
            block_buffer.string = str(file_stream.read(block_buffer.length_of_string).decode("utf-8"))
            if block_buffer.string == "": block_buffer.string = "SceneData"
            block_buffer.type = int.from_bytes(file_stream.read(4), "little")
            file_stream.seek(file_stream.tell() + 8)

            block_buffer.get_data(file_stream)
            self.blocks.update({block_buffer.string : block_buffer})

            file_count -= 1
        return

    def save(self, path):
        with open(path, "wb") as file:
            file.write(struct.pack("<i", len(self.blocks.keys())))
            for block in self.blocks.values():
                file.write(struct.pack("<i", block.offset))
                file.write(struct.pack("<i", block.size))
                file.write(struct.pack("<i", block.length_of_string))
                if block.string != "SceneData": file.write(bytes(block.string, "utf-8"))
                file.write(struct.pack("<i", block.type))
                file.write(bytearray(8))

            for block in self.blocks.values():
                file.write(block.data)

    def recalculate_offsets(self):
        offset = 4

        #calculate glossary size
        for block in self.blocks.values(): offset += 24 + block.length_of_string

        #calculate item size
        for block in self.blocks.values():
            block.offset = offset
            offset += len(block.data)


