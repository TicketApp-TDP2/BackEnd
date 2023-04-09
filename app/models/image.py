EXTENSION_SHIFT = 6  # from len('image/')


class Image:
    def __init__(
        self,
        name: str,
        content: bytes,
    ):
        self.name = name
        self.extension = self.name[EXTENSION_SHIFT:]
        self.content = content
