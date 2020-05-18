import pygame as pg

from core_funcs import world_to_chunk_vec, world_to_pix_shift
from global_params import CHUNK_SIZE, CHUNK_PIX_SIZE, C_KEY
from core import ChunkView, WorldView, PixVec, ChunkVec, WorldVec
from chunk import Chunk


class World:
    def __init__(self):
        self.chunks_existing = {}
        self.chunks_visible = {}

        self.chunk_view = ChunkView(ChunkVec(0, 0), ChunkVec(0, 0))
        self.max_view = WorldView(WorldVec(0, 0), WorldVec(0, 0))

        self.max_surf = pg.Surface((1, 1))
        self.do_init_max_surf = True
        self.max_surf.set_colorkey(C_KEY)

    def _update_chunk_view(self, camera):
        """Updates chunk_view and returns True if there are new chunks to load, False otherwise. """
        new_chunk_view = ChunkView(
            world_to_chunk_vec(camera.world_view.pos_0),
            world_to_chunk_vec(camera.world_view.pos_1),
            )

        if new_chunk_view == self.chunk_view:
            return False

        self.chunk_view = new_chunk_view
        return True

    def _load_chunks(self):
        self.max_view = WorldView(
            WorldVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(self.chunk_view.pos_0, CHUNK_SIZE)]),
            WorldVec(*[(dim+1) * chunk_size_dim for dim, chunk_size_dim in zip(self.chunk_view.pos_1, CHUNK_SIZE)]),
            )

        self.chunks_visible = {}
        for chunk_world_pos_x in range(self.max_view.pos_0.x, self.max_view.pos_1.x, CHUNK_SIZE.x):
            for chunk_world_pos_y in range(self.max_view.pos_0.y, self.max_view.pos_1.y, CHUNK_SIZE.y):
                chunk_world_pos = WorldVec(chunk_world_pos_x, chunk_world_pos_y)
                if chunk_world_pos in self.chunks_existing:
                    chunk_to_load = self.chunks_existing[chunk_world_pos]
                else:
                    chunk_to_load = Chunk(chunk_world_pos)
                    self.chunks_existing[chunk_world_pos] = chunk_to_load

                self.chunks_visible[chunk_world_pos] = chunk_to_load

    def _draw_max_surf(self):
        self._load_chunks()

        self.max_surf.fill(C_KEY)
        blit_sequence = []
        for world_pos, chunk in self.chunks_visible.items():
            max_view_world_shift = WorldVec(*(pos - shift for pos, shift in zip(world_pos, self.max_view.pos_0)))
            pix_shift = world_to_pix_shift(max_view_world_shift, CHUNK_PIX_SIZE, self.max_surf.get_size())
            blit_sequence.append((chunk.surf, pix_shift))
        self.max_surf.blits(blit_sequence)

    def _resize_max_surf(self, camera):
        max_surf_pix_size = tuple(
            (dim + 2) * pix
            for dim, pix in zip(world_to_chunk_vec(camera.world_size), CHUNK_PIX_SIZE)
            )
        self.max_surf = pg.transform.scale(self.max_surf, max_surf_pix_size)

    def draw(self, camera):
        are_new_chunks = self._update_chunk_view(camera)
        if resized := (camera.is_zooming or self.do_init_max_surf):
            self._resize_max_surf(camera)
            self.do_init_max_surf = False
        if are_new_chunks or resized:
            self._draw_max_surf()
        camera.draw_world(self.max_surf, self.max_view.pos_0)
