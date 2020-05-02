import globals
from chunk import Chunk


class World:
    def __init__(self):
        self.chunks_loaded = set()
        self.chunks_existing = set()

    def update(self, view_rect):
        chunks_needed = self.chunks_in_view_rect(view_rect)
        chunks_to_load = chunks_needed.difference(self.chunks_loaded)
        self.get_chunks(chunks_to_load)

    @staticmethod
    def world_to_chunk_coords(coords):
        return [coord//globals.CHUNK_SIZE for coord in coords]

    @staticmethod
    def chunks_in_view_rect(view_rect):
        return set()

    def get_chunks(self, chunks):
        for chunk in chunks:
            pass

    def draw(self, view_rect):
        pass
