class s3dpak():
    class block():
        def __init__(self):
            self.count = 0
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

    def __init__(self, file_stream):
        self.blocks = {}
        block_buffer = self.block()
        #initial block doesn't have 8 bytes padding
        block_buffer.count = int.from_bytes(file_stream.read(4), "little")
        block_buffer.offset = int.from_bytes(file_stream.read(4), "little")
        block_buffer.size = int.from_bytes(file_stream.read(4), "little")
        block_buffer.length_of_string = int.from_bytes(file_stream.read(4), "little")
        block_buffer.string = str(file_stream.read(block_buffer.length_of_string).decode("utf-8"))
        file_count = block_buffer.count - 1

        block_buffer.get_data(file_stream)
        self.blocks.update({block_buffer.string : block_buffer})

        while file_count > 0:
            block_buffer = self.block()
            block_buffer.count = int.from_bytes(file_stream.read(4), "little")
            file_stream.seek(file_stream.tell() + 8)
            block_buffer.offset = int.from_bytes(file_stream.read(4), "little")
            block_buffer.size = int.from_bytes(file_stream.read(4), "little")
            block_buffer.length_of_string = int.from_bytes(file_stream.read(4), "little")
            block_buffer.string = str(file_stream.read(block_buffer.length_of_string).decode("utf-8"))
            if block_buffer.string == "": block_buffer.string = "SceneData"

            block_buffer.get_data(file_stream)
            self.blocks.update({block_buffer.string : block_buffer})

            file_count -= 1
        return
