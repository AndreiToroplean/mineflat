from game import Game


class GameManager:
    def __enter__(self):
        self.game = Game()
        return self.game

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.game.exit()
