
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
import os

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveReflexAgent', second = 'DefensiveReflexAgent'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

"""
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
    self.weight['Defensive']= {}

    
    """
    self.weight['Offensive'] = {'distanceToFood': 1.0, 'distanceToCapsule':1.1,'DistanceToGhost':2.0,
                                'returnHome': 2.0}
    """

    # Set learning rate...etc
    self.epsilon = 0.4 #exploration prob
    self.alpha = 0.5 #learning rate
    self.discountRate = 0.8

    # Agent start location
    self.start = gameState.getAgentPosition(self.index)

    self.minGhost = 0.0

    CaptureAgent.registerInitialState(self, gameState)


  def chooseAction(self, gameState):
    self.readFile()
    """
    Picks among the actions with the highest Q(s,a).
    """

    # Legal Actions that you can take.
    actions = gameState.getLegalActions(self.index)

    actions.remove('Stop')

    values = [self.evaluate(gameState, a) for a in actions]

    maxValue = max(values)

    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    action = random.choice(bestActions)
    
    # flip coins here
    if len(actions) != 0:
      prob = util.flipCoin(self.epsilon)

      if prob:
        action = random.choice(actions)

    self.update(gameState, action)

    return action



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


    # We get the Q value right from here.
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)


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

  def readFile(self):
    if not os.path.exists("weight.txt"):
      fo = open("weight.txt", "w")
      fo.write("distanceToFood:0.0;distanceToCapsule:0.0;distanceToGhost:0.0;returnHome:0.0");
      fo.close()
      self.weight['Offensive'] = {'distanceToFood': 0.0, 'distanceToCapsule':0.0,'distanceToGhost':0.0,
                                'returnHome': 0.0}

    else:
      fo = open("weight.txt","r")
      string = fo.readline()
      fo.close()
      self.weight['Offensive'] = {}
      groups = string.split(';')
      for pair in groups:
        temp = pair.split(':')
        self.weight['Offensive'][temp[0]] = float(temp[1])

    """self.weight['Offensive'] = {'distanceToFood': 1.0, 'distanceToCapsule':1.1,'DistanceToGhost':2.0,
                                            'returnHome': 2.0}"""


  def writeFile(self,string):
    
    fo = open("history.txt","a")
    fo.write(str(string))
    fo.close()
            
    fo = open("weight.txt","w")
    fo.write(str(string))
    fo.close()






class OffensiveReflexAgent(ApproximateQLearningAgent):

  # (DONE&NEEDS DEBUG)If we get closer to the nearest food, then the features should be higher (smaller distance, higher feature)
  # (DONE&NEEDS DEBUG)If we get closer to the super food, then the features should be higher (smaller distance, higher feature)
  # (DONE&NEEDS DEBUG)The more food we are carrying, the distance to return home will be more important (higher food, smaller distance to home, higer feature)
  # (HALF DONE)If we get closer to the enermy, the features should be lower(smaller distance, smaller feature except they are scared or on our side)
  # Please commit here what else should be done
  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    currPos = gameState.getAgentPosition(self.index)
    myState = successor.getAgentState(self.index)
    CurrState = gameState.getAgentState(self.index)

    # ------------------------Nearest Food Feature-----------------------
    # Food that the agent can eat.
    foodList = self.getFood(successor).asList()    
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    features['distanceToFood'] = 4.5/minDistance
    # If this state eaten one food
    if len(foodList) < len(self.getFood(gameState).asList()):
      features['distanceToFood'] = 5.0
    # ------------------------End--------------------------------------



    # ------------------------Super Food Feature-----------------------
    # Get capsule location after taking this action
    nowCapsule = self.getCapsules(successor)
    # Capsule is already eaten
    if self.getCapsules(gameState) == []:
      features['distanceToCapsule'] = 0.0
    else:
      # Capsule will be eaten in this step
      if len(nowCapsule) < len(self.getCapsules(gameState)):
        features['distanceToCapsule'] = 1.1
      # Normal case
      else:
        capsuleDistance = []
        for location in nowCapsule:
          capsuleDistance.append(self.getMazeDistance(myPos,location))
        features['distanceToCapsule'] = 1/min(capsuleDistance)
    # ------------------------End--------------------------------------



    # ------------------------Enermy Distance Feature-----------------------
    # Get Enermy Index
    enermiesIndex = self.getOpponents(gameState)

    
    # Remove enermies index as pacman
    enermyDefendingIndex = enermiesIndex[:]
    for index in enermiesIndex:
      if gameState.getAgentState(index).isPacman:
        enermyDefendingIndex.remove(index)

    # Get Enermy Position which in 5 square of agent
    enermies = []
    for index in enermyDefendingIndex:
      if gameState.getAgentPosition(index)!= None:
        enermies.append(gameState.getAgentPosition(index))

    # Has defending enermy within 5 square
    if enermies !=[]:
      
      # If I am pacman need to run away
      
      enemiesDistance = []
      for location in enermies:
        enemiesDistance.append(self.getMazeDistance(myPos,location))

      features['distanceToGhost'] = min(enemiesDistance) 
      self.minGhost = min(enemiesDistance) * 0.3

      if myPos == self.start :
        features['distanceToGhost'] = -1.0

        

      newActions = successor.getLegalActions(self.index)
      newActions.remove('Stop')

      if len(newActions) == 1 and min(enemiesDistance)<= 3:
        features['distanceToGhost'] -= 1.0

      for index in enermiesIndex:
        if not gameState.getAgentState(index).scaredTimer == 0:
          features['distanceToGhost'] = 0.0
      # If I am not pacman should consider the ghoust one step away:
      

    # nosiyDistance =  gameState.getAgentDistances()
    # Does not have enermy within 5 square
    # Not Implemented

    # ------------------------End--------------------------------------



    # ------------------------Return Home Feature-----------------------
    # Get Food Carrying
    foodCarrying = CurrState.numCarrying
    distanceToHome = self.getMazeDistance(myPos, self.start)
    if not distanceToHome == 0:
      features['returnHome'] = foodCarrying * 1.0/self.getMazeDistance(myPos, self.start)
    else:
      features['returnHome'] = 0

    # This feature should be home distance * food carrying 
    # (more you are carrying, you will more need to go home)

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
  def update(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    currPos = gameState.getAgentPosition(self.index)
    currState = gameState.getAgentState(self.index)
    reward = 0.0


    # Pacman will be eaten, Punish! That is very serious!
    if myPos == self.start and currState.isPacman:
      reward = reward - 20


    # Eat food give one small reward
    foodList = self.getFood(successor).asList()
    if len(foodList) < len(self.getFood(gameState).asList()):
      reward = reward + 2

    # Eat super food give one larger reward
    # Get capsule location after taking this action
    nowCapsule = self.getCapsules(successor)
    # Capsule is already eaten
    if not self.getCapsules(gameState) == []:
      # Capsule will be eaten in this step
      if len(nowCapsule) < len(self.getCapsules(gameState)):
        reward = reward + 40




    # Closer to food, higher reward
    foodList = self.getFood(successor).asList()    
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])

    foodList1 = self.getFood(gameState).asList()    
    minDistance1 = min([self.getMazeDistance(currPos, food) for food in foodList1])

    if minDistance < minDistance1:
      reward += 1.0
    else:
      reward -= 1.0





    # score added give big reward
    scores  = successor.getScore() - gameState.getScore()

    if scores > 0 :
      reward = reward + scores * 10

    qValve = self.evaluate(gameState, action)

    actions = successor.getLegalActions(self.index)

    actions.remove('Stop')

    values = [self.evaluate(successor, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    
    difference = reward + self.discountRate * maxValue - qValve

    weights = self.weight['Offensive']

    features = self.getFeatures(gameState, action)

    print reward
    print maxValue
    print difference


    weights['distanceToFood'] = weights['distanceToFood'] + self.alpha * difference * features['distanceToFood']
    weights['distanceToCapsule'] = weights['distanceToCapsule'] + self.alpha * difference * features['distanceToCapsule']
    weights['distanceToGhost'] = weights['distanceToGhost'] + self.alpha * difference * features['distanceToGhost']
    weights['returnHome'] = weights['returnHome'] + self.alpha * difference * features['returnHome']
    print weights
    string = "distanceToFood:"+str(weights['distanceToFood'])+";"
    string+="distanceToCapsule:"+str(weights['distanceToCapsule'])+";"
    string+="distanceToGhost:"+str(weights['distanceToGhost'])+";"
    string+="returnHome:"+str(weights['returnHome'])+"\n"

    self.writeFile(string)










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
  def update(self, gameState, action):
    print ""