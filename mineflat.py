from game_manager import GameManager


def main():
    with GameManager() as game:
        game.main_loop()


if __name__ == '__main__':
    main()
