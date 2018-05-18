from captureAgents import CaptureAgent
import random, util
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.
  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
#Action base on minimax  method

  def chooseAction(self, gameState):

      enemies = [a for a in self.getOpponents(gameState) if gameState.getAgentState(a).getPosition() != None]

      def maxValue(gameState, depth):
          if depth == 0 or gameState.isOver():
              return (self.evaluationFunction(gameState), "Stop")
          
          enemy = min(enemies)
          #legal actions
          actions = gameState.getLegalActions(self.index)
          #remove none type
          actions.remove(Directions.STOP)
          successors = [gameState.generateSuccessor(self.index, action) for action in actions]
          values = [minValue(successor, enemy, depth)[0] for successor in successors]
          maxScore = max(values)
          bestMove = [index for index in range(len(values)) if values[index] == maxScore]
          move = random.choice(bestMove)

          return maxScore, actions[move]

      def minValue(gameState, enemy, depth):

          if depth == 0 or gameState.isOver():
              return (self.evaluationFunction(gameState), "Stop")
          # legal actions
          actions = gameState.getLegalActions(enemy)
          # remove none type
          actions.remove(Directions.STOP)
          successors = [gameState.generateSuccessor(enemy, action) for action in actions]
          if enemy < max(enemies):
              values = [minValue(successor, max(enemies), depth)[0] for successor in successors]
          else:
              values = [maxValue(successor, depth - 1)[0] for successor in successors]
          minScore = min(values)

          return minScore, Directions.STOP

      if len(enemies) > 0:
          action = maxValue(gameState, depth=2)[1]
      else:
          actions = gameState.getLegalActions(self.index)
          actions.remove(Directions.STOP)
          successors = [self.getSuccessor(gameState, action) for action in actions]
          values = [self.evaluationFunction(successor) for successor in successors]
          maxValue = max(values)
          action = random.choice([a for a, v in zip(actions, values) if v == maxValue])
          
      return action

  def evaluationFunction(self, gameState):
      util.raiseNotDefined()

  def getSuccessor(self, gameState, action):
      """
      Finds the next successor which is a grid position (location tuple).
      """
      successor = gameState.generateSuccessor(self.index, action)
      pos = successor.getAgentState(self.index).getPosition()
      if pos != nearestPoint(pos):
          # Only half a grid position was covered
          return successor.generateSuccessor(self.index, action)
      else:
          return successor


class DefensiveReflexAgent(DummyAgent):

    def evaluationFunction(self, gameState):

        if self.red:
            self.midWidth = (gameState.data.layout.width -1) / 2
        else:
            self.midWidth = ((gameState.data.layout.width - 1) / 2) + 1
        self.midHeight = gameState.data.layout.height / 2
        midPos = (self.midWidth,self.midHeight)
        myPos = gameState.getAgentPosition(self.index)
        distanceToMid = self.getMazeDistance(myPos, midPos)
        distanceToEnemy = 999
        seeEnemy = True
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            distanceToInvader = min(dists)
            seeEnemy = False
        else:
            distanceToInvader = distanceToMid
            minDistance = 999
            for enemy in enemies:
                enemyPos = enemy.getPosition()
                if enemyPos is not None:
                    seeEnemy  = False
                    newDistance = self.getMazeDistance(myPos,enemyPos)
                    if newDistance < minDistance:
                        minDistance = newDistance

            distanceToEnemy = minDistance

        if seeEnemy is True:
            myPos = gameState.getAgentState(self.index).getPosition()
            capsuleList = self.getCapsulesYouAreDefending(gameState)
            foodList = self.getFoodYouAreDefending(gameState).asList()
            minDistance = 0
            if len(capsuleList) > 0:
                for capsule in capsuleList:
                    dist = self.getMazeDistance(capsule, myPos)
                    minDistance += dist
                minDistance /= len(capsuleList)
            else:
                for food in foodList:
                    dist = self.getMazeDistance(food, myPos)
                    minDistance += dist
                minDistance /= len(foodList)

                distanceToEnemy = minDistance


        return -999 * len(invaders) -  9 * distanceToEnemy - 9 * distanceToInvader
