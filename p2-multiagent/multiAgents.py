# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()

        # We dont Stop while playing pacman usually
        if action == 'Stop':
            return -10000

        "food scores"
        # Closer means got higher score. So use negative number here.
        food_list = oldFood.asList()
        food_distances = []
        for food in food_list:
          food_distances.append(-(util.manhattanDistance(newPos, food)))

        if food_distances != []:
          closet_food_score = max(food_distances)

        # no food remaining, does not matter here.
        else:
          closet_food_score = 0


        "ghost scores"
        # Never Touch The Ghost!
        if newPos in [ghost.getPosition() for ghost in newGhostStates]:
          return -999999999


        return closet_food_score
def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):

        # For pacman find the best score
        def max_finder(state, current_depth):
            
            # if game end or reached the given depth, return the score
            if state.isWin() or state.isLose() or current_depth == self.depth:
              return (self.evaluationFunction(state), "Stop")


            #lowest value
            max_score = float('-Inf')
            best_move = 'Stop'

            # Pacman legal actions
            actions = state.getLegalActions(0)

            for action in actions:
              # Stop have no need to consider about
              if action == "Stop":
                continue

              # find the max score from the scores that the ghosts try to decrease
              current_score = min_finder(state.generateSuccessor(0, action), current_depth, 1)

              if current_score > max_score:
                max_score = current_score
                best_move = action

            # here returned score + action, action is used for the return to getAction
            return (max_score, best_move)

        # for ghost find the min score
        def min_finder(state,current_depth,ghost_index):

          if state.isWin() or state.isLose():
              return self.evaluationFunction(state)

          min_score = float('Inf')

          actions = state.getLegalActions(ghost_index)

          # Note: every action of every ghost should be considered
          for action in actions:

            # Is the last ghost, just loop in the actions to get the min score
            if ghost_index == state.getNumAgents()-1:

              next_max = max_finder(state.generateSuccessor(ghost_index, action), current_depth + 1 )

              min_score = min(next_max[0], min_score)

            # Still has next ghost, no need to loop this ghost's actions first, just jump to next.
            # The actions loop should begin from the last ghost
            else:

              next_ghost_min = min_finder(state.generateSuccessor(ghost_index, action),current_depth, ghost_index + 1)
              min_score = min(min_score, next_ghost_min)

          return min_score

        # start of get action
        current_depth = 0
        best_move = max_finder(gameState, current_depth)

        # best_move[0] is score
        return best_move[1]

        "Reason that not using the design below"
        # For matching format learned from lecture"
        # For designing next question easier
        
        "Another Design"
        """
        score =  float("-inf")   #the smallest number
        bestAction = None

        for action in gameState.getLegalActions(0):
            #print action

            newScore = self.gotScore(gameState.generateSuccessor(0, action), self.depth * gameState.getNumAgents() - 1)

            if score < newScore:
                score = newScore
                bestAction = action
        return bestAction

    def gotScore(self, gameState, depth):
                #reach bottom or game over
        if depth == 0 or gameState.isWin() or gameState.isLose() :
            return self.evaluationFunction(gameState)

        numberOfAgents = gameState.getNumAgents()
                # index = 0 or 1 or 2
        index = (numberOfAgents - (depth % numberOfAgents)) % numberOfAgents
        #print index

        scores = [self.gotScore(gameState.generateSuccessor(index, action), depth - 1) for action in gameState.getLegalActions(index)]
        #print scores
        #index 0 mean pacman
        if index == 0:
          return max(scores)  #max for pacman
        else:
          return min(scores)   #min for ghost
        """

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        # For pacman find the best score
        def max_finder(state, current_depth, alpha, beta):
            
            # if game end or reached the given depth, return the score
            if state.isWin() or state.isLose() or current_depth == self.depth:
              return (self.evaluationFunction(state), "Stop")


            #lowest value
            max_score = float('-Inf')
            best_move = 'Stop'

            # Pacman legal actions
            actions = state.getLegalActions(0)

            for action in actions:
              # Stop have no need to consider about
              if action == "Stop":
                continue

              # find the max score from the scores that the ghosts try to decrease
              current_score = min_finder(state.generateSuccessor(0, action), current_depth, 1, alpha, beta)

              if current_score > max_score:
                max_score = current_score
                best_move = action

              # if current score is higher than beta, then no need to take next action.
              if (max_score > beta):
                return (max_score, best_move)

              # update alpha
              alpha = max(alpha, max_score)
            # here returned score + action, action is used for the return to getAction
            return (max_score, best_move)

        # for ghost find the min score
        def min_finder(state,current_depth,ghost_index, alpha, beta):

          if state.isWin() or state.isLose():
              return self.evaluationFunction(state)

          min_score = float('Inf')

          actions = state.getLegalActions(ghost_index)

          # Note: every action of every ghost should be considered
          for action in actions:

            # Is the last ghost, just loop in the actions to get the min score
            if ghost_index == state.getNumAgents()-1:

              next_max = max_finder(state.generateSuccessor(ghost_index, action), current_depth + 1 , alpha, beta)

              min_score = min(next_max[0], min_score)

            # Still has next ghost, no need to loop this ghost's actions first, just jump to next.
            # The actions loop should begin from the last ghost
            else:

              next_ghost_min = min_finder(state.generateSuccessor(ghost_index, action),current_depth, ghost_index + 1, alpha, beta)
              min_score = min(min_score, next_ghost_min)

            # if current score is lower than alpha, there is no need to take the next action
            if min_score < alpha:
              return min_score

            # update the beta
            beta = min(min_score,beta)



          return min_score

        # start of get action
        current_depth = 0

        # init alpha and beta
        alpha = float('-Inf')
        beta = float('Inf')

        best_move = max_finder(gameState, current_depth, alpha, beta)

        # best_move[0] is score
        return best_move[1]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        score = float("-inf")  # the smallest number
        bestAction = None

        for action in gameState.getLegalActions(0):
            # print action

            newScore = self.gotScore(gameState.generateSuccessor(0, action), self.depth * gameState.getNumAgents() - 1)

            if score < newScore:
                score = newScore
                bestAction = action
        return bestAction

    def gotScore(self, gameState, depth):
        # reach bottom or game over
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)

        numberOfAgents = gameState.getNumAgents()
        # index = 0 or 1 or 2
        index = (numberOfAgents - (depth % numberOfAgents)) % numberOfAgents
        # print index

        scores = [self.gotScore(gameState.generateSuccessor(index, action), depth - 1) for action in gameState.getLegalActions(index)]
        # print scores
        if index == 0:
            return max(scores)  # max for pacman

        return 1.0 * sum(scores)/(1.0 *  len(scores))
        #test

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    import numpy
    foodPos = currentGameState.getFood().asList()

    #current pacman position
    current = list(currentGameState.getPacmanPosition())

    #food distence from all position
    foodDist = [-manhattanDistance(pos, current) for pos in foodPos]

    #if no food distance = 0
    if len(foodDist) == 0:
        foodDist.append(0)

    #return max or mean base on the probability
    if random.random() > 0.8:
        return max(foodDist) + currentGameState.getScore()
    else:
        return numpy.mean(foodDist) + currentGameState.getScore()
# Abbreviation
better = betterEvaluationFunction

