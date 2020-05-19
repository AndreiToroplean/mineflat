from game.game import Game


def main():
    with Game() as game:
        game.main_loop()


if __name__ == '__main__':
    main()
