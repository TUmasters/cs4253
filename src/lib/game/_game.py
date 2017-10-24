#!/usr/bin/env python3

import pygame
## We will use persistent data structures because we want fast
## immutable game states
from pyrsistent import m, v, pmap, PRecord
import time
import threading, asyncio
from ...lib import cli
import logging, sys

class Agent:
    def __init__(self):
        pass

    def decide(self, state):
        """Main decision function for the agent. Returns the action that the
        agent decides for the current player to perform.

        Note that the available actions at a given GameState is
        accessed via `state.actions`.

        :param GameState state: The current state of the game.
        :returns action: The desired action that the player will perform.

        """
        raise NotImplementedError

    def learn(self, states, player_id):
        """Optional function. In the special case that the agent has an
        evaluation function that it is actively learning, this
        function exists as a way of 'retrospectively' learning.

        For now, ignore this function.

        :param states: List of states that the game went through,
                       where states[0] is the initial state.
        """
        pass


class Game:
    def __init__(self, game_type, agents, display=True):
        self.game_type = game_type
        self.agents = list(agents)
        self.display = display
        self._screen_lock = asyncio.Lock()

    def run(self, display=True, play_again='query', speed=2, pause_on_turn=False):
        if display:
            pygame.init()
            screen = pygame.display.set_mode((672, 480))
        else:
            screen = None
        games = []
        game_thread = threading.Thread(target=self._run_game,
                                       args=(games, screen, play_again, speed, pause_on_turn))
        game_thread.start()
        if display:
            self._run_display(screen, game_thread)
        else:
            game_thread.join()
        return games

    def _run_game(self, games, screen=None, play_again='query', speed=2, pause_on_turn=False):
        while True:
            games += [self._run_round(speed, pause_on_turn)]
            if not play_again \
               or play_again == 'query' and not self._play_again() \
               or isinstance(play_again, int) and len(games) < play_again:
                break

    def _run_round(self, speed, pause_on_turn, screen=None):
        state = self.game_type.init(self.agents)
        states = [state]
        i = -1
        self._draw_state(state)
        if not screen:
            turn_wait = 0
            round_wait = 0
        elif speed == 2:
            turn_wait = 0
            round_wait = 10
        elif speed == 1:
            turn_wait = 50
            round_wait = 100
        else:
            turn_wait = 500
            round_wait = 1000
        while not state.is_terminal:
            new_state = None
            i = (i + 1) % len(self.agents)
            while new_state == None:
                start_t = int(round(time.time() * 1000))
                agent = self.agents[i]
                action = agent.decide(state)
                new_state = state.act(action)
                if not new_state:
                    logging.info("Invalid action performed!")
            self._draw_state(new_state)
            if new_state in states:
                logging.info("State has been repeated! Therefore, game is over.")
                break
            states += [new_state]
            state = new_state
            end_t = int(round(time.time() * 1000))
            wait_time = turn_wait - (end_t - start_t)
            if pause_on_turn:
                while True:
                    pygame.event.clear()
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            break
            if wait_time > 0 and self.display:
                pygame.time.wait(wait_time)
        for player_id, agent in enumerate(self.agents):
            agent.learn(states, player_id)
        pygame.time.wait(round_wait)
        return states

    def _run_display(self, screen, game_thread):
        clock = pygame.time.Clock()
        while game_thread.isAlive():
            with (yield from self._screen_lock):
                pygame.display.update()
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        pygame.quit()

    def _draw_state(self, state):
        if self.display:
            surf = state.draw()
            with (yield from self._screen_lock):
                self.screen.blit(surf, (0, 0))

    def _play_again(self):
        if not self.display:
            return cli.ask_yn('Play again?')
        font = pygame.font.SysFont("monospace", 32)
        font.set_bold(True)
        label = font.render("play again? (y/n)", 1, (255, 255, 255))
        window = (self.screen.get_width()/2 - 200, self.screen.get_height()/2 - 30, 400, 60)
        window_b = (window[0]-4, window[1]-4, window[2]+8, window[3]+8)
        pygame.draw.rect(self.screen, (255, 255, 255), window_b)
        pygame.draw.rect(self.screen, (0, 0, 0), window)
        with (yield from self._screen_lock):
            self.screen.blit(label, (window[0]+18, window[1]+7))
        while True:
            pygame.event.clear()
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    return False


class GameType:
    """A helper class that initializes the game state. Used as a class
    since the game type might have parameters."""
    def __init__(self):
        pass

    def init(self, agents):
        pass


class GameState(PRecord):
    """A recording of the current state of a game. The game state performs
    several functions: it contains information about the current game
    state, but also contains code for running the game via the "act"
    method. This enables the Game class to run the game in real time
    while also allowing agents to look into the future.

    When writing your agent, it should only access the functions given
    in this class.

    """

    @property
    def num_players(self):
        """Returns the number of players in the game."""
        pass

    @property
    def current_player(self):
        """Returns the ID of the current player of the game."""
        pass

    @property
    def is_terminal(self):
        """True if the game state is at a terminal node."""
        raise NotImplementedError

    @property
    def actions(self):
        """Returns the list of actions available at this state."""
        raise NotImplementedError

    def reward(self, player_id):
        """Returns the reward that the player receives at the end of the
        game.

        :param int player_id: The player id.
        :return: The reward for `player_id` if the state is terminal;
                 None otherwise.
        """
        raise NotImplementedError

    def act(self, action):
        """Returns the resultant GameState object when performing `action` in
        the current state. Since the GameState keeps track of the
        current player, there is no need to pass which player is
        performing the action.

        For further emphasis, note that this function is NOT
        DESTRUCTIVE! It returns a *new* game state for which `action`
        has been performed without changing anything in the current
        GameState object.

        You might be worried that this method will be
        inefficient. However, this class has been implemented as a
        *persistent* data structure using pyrsistent, which means that
        it has several memory- and time-based optimizations that make
        copying efficient. It will be worse than destructive updates,
        but significantly better than deep copying.

        :param Action action: The action to perform
        :return: A new GameState where action has been performed, or
                 None if the action is invalid.

        """
        raise NotImplementedError

    def _action_is_valid(self, action):
        if self.is_terminal:
            print("""ERROR: Player tried to perform an action in a terminal state. Make sure that you are performing actions solely in non-terminal states.""")
            return None

        if not action in self.actions:
            print("""ERROR: Player tried to perform an illegal action. Make sure that you only perform actions available in `state.actions`.

Action: {}
Allowed actions: {}""".format(action, self.actions))
            return None
        return self

    def draw(self):
        """Used internally for visualizing the state of the game in the Game
        class.

        :returns: A pygame.Surface image of the current game state.
        """
        raise NotImplementedError
