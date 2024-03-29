from game import Game
from util import vprint
import random

class President:
    def __init__(self, players, ranks=None):
        '''
        Class that represents a session of President, 

        A session exists out of multiple games, every game players compete to
        become the President.
        The first game all players have equal ranks but after one game they
        can become: 

        President: Receives the 2 best cards of the Scum and returns his lowest cards.
        Vice-President: Receives the best card of the High-Scum and returns his lowest card.
        Person: No extra rules here
        High-Scum: Receives the worst card of the Vice-President and returns his best cards
        Scum: Receives the 2 worst card of the President and returns his 2 best cards
        '''
        self.players = players 
        self.ranks = ranks

    def play(self):
        '''
        Function that starts the session, keeps looping until interrupted
        '''
        while True:
            game = Game(self.players, self.ranks)
            self.ranks = game.start()

            if len(self.players) < 4:
                result = f"""Game is finished: 
                    President: {self.ranks['president'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                print(result)
            else:
                result =  f"""Game is finished: 
                    President: {self.ranks['president'].name}
                    Vice-President: {self.ranks['vice_president'].name}
                    High-Scum: {self.ranks['high_scum'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                print(result)

            if not (ans := input('Play again? (y/n): ')) or ans == 'n':
                break 


    def simulate(self, games, verbose = False):
        '''
        Function that starts the session, then plays given amount of games and prints history of players' roles.
        It returns this history so that these statistics can possibly be used somewhere else.

        Parameters:
            games: int
            verbose: boolean
        '''

        print(f"Start simulations for {games} games")
        history = dict()
        for player in self.players:
            history[player] = {'p': 0, 'vp': 0, 'hs': 0, 's': 0 }

        for i in range(games):
            if False and i % 100 == 0: self.ranks = None
            game = Game(self.players, self.ranks, verbose)
            self.ranks = game.start()

            if len(self.players) < 4:
                history[self.ranks['president']]['p'] += 1
                history[self.ranks['scum']]['s'] += 1

                if verbose:
                    print("++++++++++++++++++++++++++++++++++++")
                    print(f"RESULTS:")
                    print(f"\tPresident: {self.ranks['president'].name}")
                    print(f"\tScum: {self.ranks['scum'].name}\n")

            else:
                history[self.ranks['president']]['p'] += 1
                history[self.ranks['vice_president']]['vp'] += 1
                history[self.ranks['high_scum']]['hs'] += 1
                history[self.ranks['scum']]['s'] += 1

                if verbose:
                    print("++++++++++++++++++++++++++++++++++++")
                    print(f"RESULTS:")
                    print(f"\tPresident: {self.ranks['president'].name}")
                    print(f"\tVice-President: {self.ranks['vice_president'].name}")
                    print(f"\tHigh-Scum: {self.ranks['high_scum'].name}")
                    print(f"\tScum: {self.ranks['scum'].name}\n")

        print("\n++++++++++++++++++++++++++++++++++++")
        print("Simulation finished")
        print("++++++++++++++++++++++++++++++++++++")

        for player in self.players:
            if len(self.players) < 4:
                result = f"""
                Player {player.name}
                    President: {history[player]['p']} times
                    Scum: {history[player]['s']} times
                    W/L: {round(history[player]['p']/games*100, 2)}%"
                """
                print(result)
            else:
                result = f"""
                Player {player.name}
                    President: {history[player]['p']} times
                    Vice-President: {history[player]['vp']} times
                    High-Scum: {history[player]['hs']} times
                    Scum: {history[player]['s']} times
                    W/L: {round(history[player]['p']/games*100, 2)}%"
                    """
                print(result)

        return history

    def train(self, games, show_every=None):
        '''
        Method that runs a number of games to train agents

        Parameters:
            games: int
            show_every: int
        '''
        for i in range(games):
            if show_every and ( i % show_every == 0):
                print(f"Trained for {i} games")
            #random.shuffle(self.players)
            if True and i % 100 == 0: self.ranks = None # reset ranks when playing against heuristic!
            game = Game(self.players, self.ranks, False)
            self.ranks = game.start()
            
    def t_input(self, container):
        inp = input()
        while inp != 'stop':
            time.sleep(1)
            inp = input()
        container.append(1)

    def train_with_cancel(self, show_every=None):
        '''
        Method that runs a number of games to train agents

        Parameters:
            games: int
            show_every: int
        '''
        container = []
        t = threading.Thread(target=self.t_input, args=(container,))
        t.start()

        i = 0
        while not container:
            if show_every and ( i % show_every == 0):
                print(f"Trained for {i} games")
            random.shuffle(self.players)
            game = Game(self.players, None, False)
            self.ranks = game.start()
            i+=1