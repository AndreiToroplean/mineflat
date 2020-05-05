import pygame as pg

from core_funcs import world_to_chunk_vec, world_to_pix_shift
from global_params import CHUNK_SIZE, CHUNK_PIX_SIZE, C_KEY
from core import ChunkView, WorldView, PixVec, ChunkVec, WorldVec
from chunk import Chunk


class World:
    def __init__(self, camera):
        self.camera = camera

        self.chunks_existing = {}
        self.chunks_visible = {}

        self.chunk_view = ChunkView(ChunkVec(0, 0), ChunkVec(0, 0))
        self.max_view = WorldView(WorldVec(0, 0), WorldVec(0, 0))

        max_surf_pix_size = tuple((dim+1) * pix
            for dim, pix in zip(world_to_chunk_vec(self.camera.world_size), CHUNK_PIX_SIZE))
        self.max_surf = pg.Surface(max_surf_pix_size)
        self.max_surf.set_colorkey(C_KEY)

    def update_chunk_view(self):
        """Updates chunk_view and returns True if there are new chunks to load, False otherwise. """
        new_chunk_view = ChunkView(
            world_to_chunk_vec(self.camera.world_view.pos_0),
            world_to_chunk_vec(self.camera.world_view.pos_1),
            )

        if new_chunk_view == self.chunk_view:
            return False

        self.chunk_view = new_chunk_view
        return True

    def load_chunks(self):
        self.max_view = WorldView(
            WorldVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(self.chunk_view.pos_0, CHUNK_SIZE)]),
            WorldVec(*[(dim+1) * chunk_size_dim for dim, chunk_size_dim in zip(self.chunk_view.pos_1, CHUNK_SIZE)]),
            )

        for chunk_world_pos_x in range(self.max_view.pos_0.x, self.max_view.pos_1.x, CHUNK_SIZE.x):
            for chunk_world_pos_y in range(self.max_view.pos_0.y, self.max_view.pos_1.y, CHUNK_SIZE.y):
                chunk_world_pos = WorldVec(chunk_world_pos_x, chunk_world_pos_y)
                if chunk_world_pos in self.chunks_existing:
                    chunk_to_load = self.chunks_existing[chunk_world_pos]
                else:
                    chunk_to_load = Chunk(chunk_world_pos)
                    self.chunks_existing[chunk_world_pos] = chunk_to_load

                self.chunks_visible[chunk_world_pos] = chunk_to_load

    def draw_max_surf(self):
        self.load_chunks()

        self.max_surf.fill(C_KEY)
        blit_sequence = []
        for world_pos, chunk in self.chunks_visible.items():
            max_view_world_shift = WorldVec(*(pos - shift for pos, shift in zip(world_pos, self.max_view.pos_0)))
            pix_shift = world_to_pix_shift(max_view_world_shift, self.max_surf.get_size(), CHUNK_PIX_SIZE)
            blit_sequence.append((chunk.surf, pix_shift))
        self.max_surf.blits(blit_sequence)

    def draw(self):
        are_new_chunks = self.update_chunk_view()
        if are_new_chunks:
            self.draw_max_surf()
        self.camera.draw_world(self.max_surf, self.max_view.pos_0)


def main():
    camera = Camera()
    camera.pos = WorldVec(0, 60)
    world = World(camera)
    world.draw()
    pg.display.flip()
    time.sleep(2)


if __name__ == "__main__":
    import time
    from camera import Camera
    main()
