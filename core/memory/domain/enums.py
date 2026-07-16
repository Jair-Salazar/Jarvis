from enum import Enum

class MemoryType(Enum):
    WORKING = "working"      # conversación actual, vive en RAM
    EPISODIC = "episodic"    # "qué pasó y cuándo"
    SEMANTIC = "semantic"    # hechos atemporales sobre el usuario