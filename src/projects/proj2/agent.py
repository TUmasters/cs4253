#!/usr/bin/env python3

from ...lib.game import Agent, RandomAgent

class MinimaxAgent(RandomAgent):
    """An agent that makes decisions using the Minimax algorithm, using a
    evaluation function to approximately guess how good certain states
    are when looking far into the future.

    :param evaluation_function: The function used to make evaluate a
        GameState. Should have the parameters (state, player_id) where
        `state` is the GameState and `player_id` is the ID of the
        player to calculate the expected payoff for.

    :param alpha_beta_pruning: True if you would like to use
        alpha-beta pruning.

    :param max_depth: The maximum depth to search using the minimax
        algorithm, before using estimates generated by the evaluation
        function.
    """
    def __init__(self, evaluate_function, alpha_beta_pruning=False, max_depth=5):
        super().__init__()
        self.evaluate = evaluate_function
        self.alpha_beta_pruning = alpha_beta_pruning
        self.max_depth = max_depth

    def decide(self, state):
        # TODO: Implement this agent!
        #
        # Read the documentation in /src/lib/game/_game.py for
        # information on what the decide function does.
        #
        # Do NOT call the soccer evaluation function that you write
        # directly from this function! Instead, use
        # `self.evaluate`. It will behave identically, but will be
        # able to work for multiple games.
        #
        # Do NOT call any SoccerState-specific functions! Assume that
        # you can only see the functions provided in the GameState
        # class.
        #
        # If you would like to see some example agents, check out
        # `/src/lib/game/_agents.py`.

        if not self.alpha_beta_pruning:
            return self.minimax(state, state.current_player)
        else:
            return self.minimax_with_ab_pruning(state, state.current_player)

    def minimax(self, state, player, depth=1):
        # This is the suggested method you use to do minimax.  Assume
        # `state` is the current state, `player` is the player that
        # the agent is representing (NOT the current player in
        # `state`!)  and `depth` is the current depth of recursion.
        return super().decide(state)

    def minimax_with_ab_pruning(self, state, player, depth=1,
                                alpha=float('inf'), beta=-float('inf')):
        return super().decide(state)

class MonteCarloAgent(RandomAgent):
    """An agent that makes decisions using Monte Carlo Tree Search (MCTS),
    using an evaluation function to approximately guess how good certain
    states are when looking far into the future.

    :param evaluation_function: The function used to make evaluate a
        GameState. Should have the parameters (state, player_id) where
        `state` is the GameState and `player_id` is the ID of the
        player to calculate the expected payoff for.

    :param max_playouts: The maximum number of playouts to perform
        using MCTS.
    """
    def __init__(self, evaluate_function, max_playouts=100):
        super().__init__()
        self.evaluate = evaluate_function
        self.max_playouts = max_playouts

    def decide(self, state):
        # TODO: Implement this agent!
        #
        # Read the documentation in /src/lib/game/_game.py for
        # information on what the decide function does.
        #
        # Do NOT call the soccer evaluation function that you write
        # directly from this function! Instead, use
        # `self.evaluate`. It will behave identically, but will be
        # able to work for multiple games.
        #
        # Do NOT call any SoccerState-specific functions! Assume that
        # you can only see the functions provided in the GameState
        # class.
        #
        # If you would like to see some example agents, check out
        # `/src/lib/game/_agents.py`.

        return self.monte_carlo(state, state.current_player)

    def monte_carlo(self, state, player):
        # This is the suggested method you use to do MCTS.  Assume
        # `state` is the current state, `player` is the player that
        # the agent is representing (NOT the current player in
        # `state`!).
        return super().decide(state)

