import csv


class CsrMap:
    def __init__(self, filename):
        self._filename = filename
        self.address = {}
        self.size = {}
        self.mode = {}
        if filename is not None:
            reader = csv.reader(open(filename))
            for row in reader:
                name = row[0]
                self.address[name] = int(row[1], 0)
                self.size[name] = int(row[2])
                self.mode[name] = str(row[3])

    def __getitem__(self, item):
        return self.address[item], self.size[item], self.mode[item]
