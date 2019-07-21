
class NeuralArea:
    """
    Neural area contains neural assemblies and undermines their properties and connectivity with other assemblies
    """
    def __init__(self, name: str):
        self.name = name
        self.modalities = []