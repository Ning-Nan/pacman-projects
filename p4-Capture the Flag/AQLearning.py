
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
    self.weight['Offensive'] = {}
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

    #print "features: ",features
    #print "weights: ",weights
    #print "result: ", features*weights

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

  # If we get closer to the nearest food, then the features should be higher (smaller distance, higher feature)
  # If we get closer to the super food, then the features should be higher (smaller distance, higher feature)
  # The more food we are carrying, the distance to return home will be more important (higher food, smaller distance to home, higer feature)
  # If we get closer to the enermy, the features should be lower(smaller distance, smaller feature except they are scared or on our side)
  # 
  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  # Not Implemented
  def getWeights(self, gameState, action):
    return self.weight['Offensive']


  """
  Method to update weight. 
  """
  # Score should be considerd as reward
  # if turned to super state should be given reward
  # if ate ernemy should be given reward
  # if died shoud be punish
  # if 
  def update(self,state):
    print "Give reward and update weights here!!"





















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
    print "Give reward and update weights here!!"
