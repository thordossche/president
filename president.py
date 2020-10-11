from game import Game
from basicPlayer  import BasicPlayer
from util import vprint

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
                result = f"""
                Game is finished: 
                    President: {self.ranks['president'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                print(result)
            else:
                result = f"""
                Game is finished: 
                    President: {self.ranks['president'].name}
                    Vice-President: {self.ranks['vice_president'].name}
                    High-Scum: {self.ranks['high_scum'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                print(result)

            if not (ans := input('Play again? (y/n): ')) or ans == 'n':
                break 


    def simulate(self, games, verbose = True):
        '''
        Function that starts the session, then plays given amount of games and prints history of players' roles.
        It returns this history so that these statistics can possibly be used somewhere else.
        '''

        history = dict()
        for player in players:
            history[player] = {'p': 0, 'vp': 0, 'hs': 0, 's': 0 }

        for _ in range(games):
            game = Game(self.players, self.ranks, verbose)
            self.ranks = game.start()

            if len(self.players) < 4:
                history[self.ranks['president']]['p'] += 1
                history[self.ranks['scum']]['s'] += 1

                result = f"""
                Game is finished: 
                    President: {self.ranks['president'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                vprint(result, verbose)

            else:
                history[self.ranks['president']]['p'] += 1
                history[self.ranks['vice_president']]['vp'] += 1
                history[self.ranks['high_scum']]['hs'] += 1
                history[self.ranks['scum']]['s'] += 1

                result = f"""
                Game is finished: 
                    President: {self.ranks['president'].name}
                    Vice-President: {self.ranks['vice_president'].name}
                    High-Scum: {self.ranks['high_scum'].name}
                    Scum: {self.ranks['scum'].name}
                    """
                vprint(result, verbose)

        for player in players:
            if len(self.players) < 4:
                result = f"""
                Player {player.name}
                    President: {history[player]['p']} times
                    Scum: {history[player]['s']} times
                """
                print(result)
            else:
                    result = f"""
                    Player {player.name}
                        President: {history[player]['p']} times
                        Vice-President: {history[player]['vp']} times
                        High-Scum: {history[player]['hs']} times
                        Scum: {history[player]['s']} times
                        """
                    print(result)

        return history

        
if __name__ == '__main__':
    players = [BasicPlayer("Player1"), BasicPlayer("Player2")]
    players.append(BasicPlayer("Player3"))
    #players.append(BasicPlayer("Player4"))
    #players.append(BasicPlayer("Player5"))
   
    session = President(players)
    #session.play()
    session.simulate(10, False)
