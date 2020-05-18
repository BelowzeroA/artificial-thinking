
class InterAreaMessage:
    """
    Storage packet for information exchange between neural areas
    """
    def __init__(self, name: str):
        self.name = name
        self.data: dict = None
