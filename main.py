#!/usr/bin/python
import os
from player import Player


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='race', const='race', nargs='?', choices=('race', 'elemination', 'football'), help='Selected gamemode (default: %(default)s)')
    parser.add_argument('--two_pods', action='store_true', help='Two player pods')
    parser.add_argument('--team', action='store_true', help='Teams')
    parser.add_argument('--debug', action='store_true', help='Do debug print for player1')
    parser.add_argument('--map', default='map1', help='Selected map for races, options: map1, map2, random1, random2')
    parser.add_argument('--no_viz', action='store_true', help='Dont show vizualization')
    parser.add_argument('players', nargs=argparse.REMAINDER)
    args, unknown = parser.parse_known_args()

    print(args)
    print(unknown)

    for player_path in args.players:
        if not os.path.isfile(player_path): 
            print("path is not an executable file: {}".format(player_path))
            exit(-1)

    players = []
    for player_path in args.players:
        player = Player(player_path, debug_print = args.debug)
        players.append(player)
        args.debug = False
 

    if not players:
        base_path = os.path.dirname(os.path.realpath(__file__))
        bot_path = os.path.join(base_path, "bots", "example_bot", "example_bot.py")
        player1 = Player(bot_path, debug_print = args.debug)
        player2 = Player(bot_path)
        player3 = Player(bot_path)
        player4 = Player(bot_path)
        players = [player1, player2, player3, player4]
        # players = [player1, player2]

    if args.mode == 'race':
        from gamemodeRace import GameModeRace
        game = GameModeRace(players, args.two_pods, args.team, args.map)
    if args.mode == 'elemination':
        from gamemodeElemination import GameModeElemination
        game = GameModeElemination(players, args.two_pods, args.team)
    if args.mode == 'football':
        from gamemodeFootball import GameModeFootball
        game = GameModeFootball(players, args.two_pods, args.team)

    if args.no_viz:
        game.run_without_vizualization()
    else:
        game.run()

    for p in players:
        p.terminate()
