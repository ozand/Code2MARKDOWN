"""
RooCode Memory Management System
"""


class MemoryBank:
    def __init__(self):
        self.memory = {}

    def store(self, key, value):
        """Store a memory entry"""
        self.memory[key] = value

    def retrieve(self, key):
        """Retrieve a memory entry"""
        return self.memory.get(key)

    def list_entries(self):
        """List all memory entries"""
        return list(self.memory.keys())
