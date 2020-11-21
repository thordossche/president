import torch
import random
from itertools import count
from collections import deque
from player import Player
from move import Move
from card import Card
from move_generator import MoveGenerator
from qtable import QTable
from random import randint
from skip import Skip

N_ACTIONS = 13*4 + 1 
SKIP = (0,0)
START = (3,0)

output_to_action_mapping = [ SKIP ] + [ (rank, amount) for rank in range(3,16) for amount in range(1,5) ]

class PresidentNetwork(torch.nn.Module):
    def __init__(self, hidden_nodes):
        super(PresidentNetwork, self).__init__()
        self.linear1 = torch.nn.Linear(15, hidden_nodes)
        self.linear2 = torch.nn.Linear(hidden_nodes, N_ACTIONS)
    
    def forward(self, x):
        x = torch.nn.functional.relu(self.linear1(x))
        return self.linear2(x)


class DeepQLearningAgent(Player):
    '''
    Player class that implements a deep Q learning agent
    '''
    def __init__(self, name, train = False):
        super().__init__(name)
        self.train = train
        self.name = name
        self.BATCH_SIZE = 16 
        self.MEM_SIZE = 50000
        self.GAMMA = 0.99
        self.EPS_END = 0.05
        self.eps = 1.0
        self.EPS_DECAY = 0.99
        self.N_ACTIONS = N_ACTIONS 
        self.network = PresidentNetwork(132)
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=1e-3)
        self.memory = deque(maxlen=self.MEM_SIZE)
        self.last_action = None
        self.last_action_illegal = False
        self.last_state = None
        self.done = False
    
    def set_training(self,train):
        self.train = train

    def play(self, last_move):
        '''
        Overwriting parent method
        '''
        possible_moves = MoveGenerator().generate_possible_moves(self.cards, last_move)
        possible_moves.append(Skip())
                                           
        state = self.get_state(last_move)

        # depending on if we want to train the agent or not, use different methods
        if not self.train:
            action = self.actual_play(torch.tensor([state]).float())
        else:
            action = self.test_play(state)

        #safe this action and state so we can use them when we get the new state, also reset last_action_illegal
        self.last_action = action
        self.last_state = state
        self.last_action_illegal = False
        next_move = self.action_to_move(action, possible_moves)

        # if move is impossible, let move be a skip and remember we played an illegal action
        if next_move == -1:
            next_move = Skip()
            self.last_action_illegal = True

        if not next_move is Skip():
            cards_to_play = next_move.cards 
            self.cards = list(filter(lambda card: card not in cards_to_play, self.cards))

        return next_move 

    # state moet tensor zijn!
    def actual_play(self, state):
        # of action = torch.argmax(network(state)).item()
        action = self.select_action(state, 0)
        actual = output_to_action_mapping[action]
        return actual

    def test_play(self, _state):
        # _state is de state dus [ .. ] maar nog niet in een tensor!
        print(_state)
        ep_reward = 0
        eps = 1.0 #moet eig globale var zijn, zie dqn.ipybn

        # if we didn't do anything yet, generate a random move
        # hoe groot kiezen we de eps?
        if self.last_action == None: 
            return self.select_action(torch.tensor([_state]).float(), 0.5)

        for t in count():
            print(count())
            # Select and perform an action
            action = self.last_action 
            done = self.done #if the game is over
            reward = self.get_reward(_state)
            state = torch.tensor([self.last_state])
            next_state = torch.tensor([_state])

            # next_state, reward, done, _ = env.step(action)
            ep_reward += reward

            # Store the transition in memory
            self.memory.append((state, action, reward, next_state, int(done)))

            # Move to the next state
            state = next_state

            # Experience replay
            if len(self.memory) >= self.BATCH_SIZE:
                batch = random.sample(self.memory, self.BATCH_SIZE)
                states, actions, rewards, n_states, dones = zip(*batch)
                state_batch = torch.cat(states,0)
                action_batch = torch.tensor(actions)
                reward_batch = torch.tensor(rewards)
                n_states = torch.cat(n_states)
                dones = torch.tensor(dones)
                
                # EXPERIENCE REPLAY
                
                # Bereken de Q-values voor de gegeven toestanden
                curr_Q = self.network(state_batch.float()).gather(1, action_batch.unsqueeze(1))
                curr_Q = curr_Q.squeeze(1)
                            
                # Bereken de Q-values voor de volgende toestanden (n_states)
                max_next_Q = (1-dones) * self.network(n_states.float()).max(1)[0].detach()

                # Gebruik deze Q-values om targets te berekenen
                targets = reward_batch + (self.GAMMA*max_next_Q)
                
                # Bereken de loss
                loss_fn = torch.nn.MSELoss()
                loss = loss_fn(curr_Q, targets)
                self.optimizer.zero_grad()
                loss.backward()
                
                # Voer een optimalisatiestap uit
                self.optimizer.step()

            # Decay exploration rate
            eps *= self.EPS_DECAY
            eps = max(self.EPS_END, eps)

            if done: 
                break

        return self.select_action(torch.tensor(_state), eps)


    def select_action(self, state, eps):
        sample = random.random() #Return the next random floating point number in the range [0.0, 1.0).
        if sample > eps:
            with torch.no_grad():
                return self.network(state).argmax().item()
        else:
            # kies random actie zonder te kijken naar state
            # uiteindelijk zal de ai leren welke acties wel en niet mogen door rewards ?
            return random.randrange(self.N_ACTIONS)    

    def get_reward(self, state):
        start_score = self.get_hand_score(self.last_state) 
        current_score = self.get_hand_score(state)
        return current_score/start_score

    def get_hand_score(self, state):
        return sum([i*state[i-1] for i in range(1,14)]) / sum(state[:13])


    def get_state(self, move):
        '''
        Method 

        Parameters:
            move: Move
        Returns:
            move: [ amount_3 amount_4 ... value_last amount_last ]
        '''
        if move is Skip():
            return self.cards_to_list() + [ 0, 0 ]
        if move.is_round_start():
            return self.cards_to_list() + [ 3, 0 ]
        return self.cards_to_list() + [move.rank, move.amount]

    def cards_to_list(self):
        card_count = 13
        cards = [ 0 for _ in range(card_count) ]

        for card in self.cards:
            if card.rank == 2:
                cards[card_count-1] += 1
            else:
                cards[card.rank-3] += 1
        
        return cards

    def move_to_action(self, move):
        '''
        Method that transforms a Move to a tuple used for indexing the QTable

        Parameters:
            move: Move
        Returns:
            action: (rank, amount)
        '''
        if move is Skip():
            return  SKIP
        return (move.rank, move.amount)

    def action_to_move(self, action, possible_moves):
        '''
        Method that seeks the move corresponding to a action

        Parameters:
            action: (rank, amount)
            possible_moves: [Move]
        Returns:
            move: Move
        '''
        # todo: for now is dit de oplossing voor illegale moves gekozen door het netwerk
        l = list(filter(lambda move: self.move_to_action(move) == action, possible_moves))
        if len(l) == 0: return -1
        else: return l[0]

    def notify_game_end(self, rank):
       #TODO: gebruik ranking mss ook in reward functie
       self.done = True 
        


