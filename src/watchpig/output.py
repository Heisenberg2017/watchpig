
class OutputBase:
    def __init__(self):
        self.output_buffer = []

    def __call__(self, obj):
        self.write(obj)

    def write(self, obj):
        pass

    def clear(self):
        self.output_buffer = []
