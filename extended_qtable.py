from pprint import pprint
from skip import Skip
from pprint import pprint

class ExtendedQTable:
    def __init__(self):
        self.table = { state: { action: 0 for action in self.possible_actions(state) } for state in self.possible_states() }
        for i in range(1, 6):
            self.table[(0,0,i)] = { action: 0 for action in self.possible_actions((2, 1, i)) }
        skip = Skip()

        for key in self.table:
            self.table[key][skip] = -1
        
        for state in self.table:
            for action in self.table[state]:
                if not state is skip and not action is skip:
                    if state[2] == action[1]:
                        self.table[state][action] = 10

        self.table[None] = { None: 0 }
    
    def possible_states(self):
        '''
        Generate all possible states
        '''
        return [ (rank, amount, amount_cards) for rank in range(3, 16) for amount in range(1, 5) for amount_cards in range(1, 6) ]
    
    def possible_actions(self, state):
        '''
        Generate all possible actions given a state

        Parameters:
            state: (rank, amount)
        Returns:
            actions: [(rank, amount)]
        '''
        if state[0] == 7:
            actions = [ (rank, amount) for rank in range(3, 8) for amount in range(1, 5) \
                    if amount >= state[1] and rank <= 7 and amount <= state[2]]

            actions_full_jokers = [(15, amount) for amount in range(1, 5) if amount >= state[1] and amount <= state[2]]
            return actions + actions_full_jokers
        else:
            return [ (rank, amount) for rank in range(3, 16) for amount in range(1, 5) \
                    if amount >= state[1] and rank >= state[0] and amount <= state[2]]
    
    def show(self):
        '''
        Method that prints the QTable
        '''
        for state in self.table.keys():
            if state == (0,):
                print(f"State: roundstart")
            elif state: # skip for None state
                print(f"State: {state}")
            for action in self.table[state]:

                if action and self.table[state][action]:
                    print(f" {action}: {round(self.table[state][action], 2)}")
            if state: # skip for None state
                print()
                print()

    def __getitem__(self, arg):
        return self.table[arg]
