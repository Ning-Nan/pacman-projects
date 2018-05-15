
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

"""
Some points:
  
  Reward given every action. Weight updated every action

  To Run: python capture.py -r AQLearning

"""
class ApproximateQLearningAgent(CaptureAgent):
  """
      Class that will use ApproximateQLearning approch.
      Training result will save as txt file.(Hard Coding maybe for now.)
  """
 
  def registerInitialState(self, gameState):
    # Weight using dictionary
    self.weight = {}
    self.weight['Offensive'] = {'distanceToFood': 1.0, 'distanceToCapsule':1.1}
    self.weight['Defensive'] = {}

    # Set learning rate...etc
    self.epsilon = 0.2 #exploration prob
    self.alpha = 0.3 #learning rate
    self.discountRate = 0.8

    # Agent start location
    self.start = gameState.getAgentPosition(self.index)


    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    # debug purpose
    if self.__class__ == OffensiveReflexAgent:
      print "Offensive Data Begin---------------------------"

    # Legal Actions that you can take.
    actions = gameState.getLegalActions(self.index)


    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)

    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    action = random.choice(bestActions)
    
    # flip coins here
    if len(actions) != 0:
      prob = util.flipCoin(self.epsilon)

      if prob:
        action = random.choice(actions)

    self.update(gameState)

    # debug purpose
    if self.__class__ == OffensiveReflexAgent:
      print "Action take: ", action
      print "END-------------------------------"
    return action


  """
  Game State after taking that action.
  """
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


  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """

    # Q(s,a) = w1f1(s,a)+w2f2(s,a)+wnfn(s,a)...

    # We get the Q value right from here.
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    # debug purpose
    if self.__class__ == OffensiveReflexAgent:
      print "features: ",features
      print "weights: ",weights
      print "result: ", features*weights
      print "action: ", action

    return features * weights


  """
  This method will be called at the end of the game.
  We should print final weight here.
  Here we just use hard coding.
  So print the updated weight, and take it from console to hard coding.
  """
  def final(self, state):
    print self.getScore(state)
    print "Not Implemented"


 






class OffensiveReflexAgent(ApproximateQLearningAgent):

  # (DONE&NEEDS DEBUG)If we get closer to the nearest food, then the features should be higher (smaller distance, higher feature)
  # (NOT DONE)If we get closer to the super food, then the features should be higher (smaller distance, higher feature)
  # (NOT DONE)The more food we are carrying, the distance to return home will be more important (higher food, smaller distance to home, higer feature)
  # (NOT DONE)If we get closer to the enermy, the features should be lower(smaller distance, smaller feature except they are scared or on our side)
  # Please commit here what else should be done
  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()

    # ------------------------Nearest Food Feature-----------------------
    # Food that the agent can eat.
    foodList = self.getFood(successor).asList()    
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    features['distanceToFood'] = 100.0/minDistance
    # If this state eaten one food
    if len(foodList) < len(self.getFood(gameState).asList()):
      features['distanceToFood'] = 150.0
    # ------------------------End--------------------------------------



    # ------------------------Super Food Feature(NOT DONE)-----------------------
    # Get capsule location after taking this action
    nowCapsule = self.getCapsules(successor)
    # Capsule is already eaten
    if self.getCapsules(gameState) == []:
      features['distanceToCapsule'] = 0.0
    else:
      # Capsule will be eaten in this step
      if nowCapsule == []:
        features['distanceToCapsule'] = 250.0
      # Normal case
      else:
        capsuleDistance = self.getMazeDistance(myPos,nowCapsule[0])
        features['distanceToCapsule'] = 150.0/capsuleDistance
    # ------------------------End--------------------------------------





    return features





  # Not Implemented
  def getWeights(self, gameState, action):
    return self.weight['Offensive']


  """
  Method to update weight and give rewards. 
  """
  # (NOT DONE)Score should be considerd as reward
  # (NOT DONE)if turned to super state should be given reward
  # (NOT DONE)if ate ernemy should be given reward
  # (NOT DONE)if died shoud be punish
  # (NOT DONE)if stop then punish
  # Please commit here what else should be done
  def update(self,state):
    print ""


























class DefensiveReflexAgent(ApproximateQLearningAgent):


  # Not Implemented
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  # Not Implemented
  def getWeights(self, gameState, action):
    return self.weight['Defensive']


  """
  Method to update weight. 
  """
  def update(self,state):
    print ""
