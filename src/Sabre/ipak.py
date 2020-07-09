# This Python file uses the following encoding: utf-8
from PySide2 import QtWidgets
from os import system, remove

ipak_to_actual_dxtype = {
"AXT1" : "bc1",
"OXT1" : "bc1",
"XT3" : "bc2",
"XT5" : "bc3",
"DXT5A" : "bc4",
"DXN" : "bc5u",
#"AI88" : "",
#"XRGB8888" : "",
#"ARGB8888" : "none right now, test this out at some point"
}

class ipak:
    class block():
        class head():
            def __init__(self, ipak_stream):
                ipak_stream.read(58) #burn for now

        def __init__(self, ipak_stream, format, width, height):
            self.format = format
            self.type = format #hacky fix this
            self.width = width
            self.height = height

            self.string = str(ipak_stream.read(264).decode("ascii")).rstrip('\0')
            ipak_stream.read(44) #burn unrequired data
            self.size = int.from_bytes(ipak_stream.read(4), "little")
            self.offset = int.from_bytes(ipak_stream.read(4), "little")
            ipak_stream.read(12) #burn the rest

            pos = ipak_stream.tell()
            ipak_stream.seek(self.offset)
            self.header = self.head(ipak_stream)
            self.data = ipak_stream.read(int(self.size))
            ipak_stream.seek(pos)

        def extract(self, location):
            with open(location + "/" + self.string, "wb") as file:
                file.write(self.data)
            dxformat = ipak_to_actual_dxtype.get(self.format, None)
            if not dxformat: return
            system('Rawtex\\RawtexCmd.exe "' + location + "\\" + self.string + '" ' + dxformat + " 0 " + self.width + " " + self.height)
            remove(location + "\\" + self.string)


    def __init__(self, ipak_stream, csv_stream):
        IPAK_STARTING_OFFSET = 0x00290008

        self.image_meta = []
        self.process_image_meta(csv_stream)

        self.blocks = {}
        count = int.from_bytes(ipak_stream.read(4), "little")
        ipak_stream.read(4) #burn padding

        for i in range(len(self.image_meta) - 1):
            self.blocks.update({self.image_meta[i][0] : self.block(ipak_stream, self.image_meta[i][2],
                                                                   self.image_meta[i][3], self.image_meta[i][4])})

    def process_image_meta(self, csv_stream):
        test = []
        for line in csv_stream:
            self.image_meta.append(line.rstrip("\n").split(","))
