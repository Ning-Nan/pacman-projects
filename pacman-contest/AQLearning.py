
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
from game import Grid
import game
from util import nearestPoint
import os


def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

"""
To Run: python capture.py -r AQLearning

"""
class MixAgent(CaptureAgent):
  """
      Class that will use ApproximateQLearning approch.
      Training result will save as txt file.(Hard Coding maybe for now.)
  """
 
  def registerInitialState(self, gameState):

    self.weight = {}
    self.weight['Defensive']= {}
    
    """
    Back up weights for testing purpose
    self.weight['Offensive'] = {'distanceToFood': 1.0, 'distanceToCapsule':1.1,'DistanceToGhost':2.0,
                                'returnHome': 2.0}
    distanceToFood:21.1358828621;distanceToCapsule:72.076020285;distanceToGhost:-7.24735154835;returnHome:3.95426736099
    """

    # Set learning rate...etc
    self.epsilon = 0.1 #exploration prob
    self.alpha = 0.3 #learning rate
    self.discountRate = 0.95

    # Agent start location
    self.start = gameState.getAgentPosition(self.index)

    self.minGhost = 0.0

    CaptureAgent.registerInitialState(self, gameState)


  def chooseAction(self, gameState):

    self.readFile()

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
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)


    return features * weights


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



  def writeFile(self,string):
    
    fo = open("history.txt","a")
    fo.write(str(string))
    fo.close()
            
    fo = open("weight.txt","w")
    fo.write(str(string))
    fo.close()






class OffensiveReflexAgent(MixAgent):

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
    if not len(foodList) == 0:   
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = 1.0/minDistance
      # If this state eaten one food
      if len(foodList) < len(self.getFood(gameState).asList()):
        features['distanceToFood'] = 1.1
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
        features['distanceToCapsule'] = 1.0/min(capsuleDistance)

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
      if not min(enemiesDistance) == 0:
        features['distanceToGhost'] = 1.0/min(enemiesDistance) 
        self.minGhost = min(enemiesDistance)

      if myPos == self.start :
        features['distanceToGhost'] = 1.0

        

      newActions = successor.getLegalActions(self.index)
      newActions.remove('Stop')

      if len(newActions) == 1 and min(enemiesDistance)<= 3:
        features['distanceToGhost'] = 1.0

      for index in enermiesIndex:
        if not successor.getAgentState(index).scaredTimer == 0:
          features['distanceToGhost'] = 0.0
      # If I am not pacman should consider the ghoust one step away:
      

    # nosiyDistance =  gameState.getAgentDistances()
    # Does not have enermy within 5 square
    # Not Implemented

    # ------------------------End--------------------------------------



    # ------------------------Return Home Feature-----------------------
    # Get Food Carrying
    foodCarrying = myState.numCarrying
    distanceToHome = self.getMazeDistance(myPos, self.start)
    if not distanceToHome == 0:
      features['returnHome'] = foodCarrying * 15.0/self.getMazeDistance(myPos, self.start)
    else:
      features['returnHome'] = 0

    if myState.isPacman and foodCarrying > 0 :
      features['returnHome'] += 1.0
    # This feature should be home distance * food carrying 
    # (more you are carrying, you will more need to go home)

    # ------------------------End--------------------------------------


    return features


  def getWeights(self, gameState, action):
    return self.weight['Offensive']


  """
  Method to update weight and give rewards. 
  """
  def update(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    currPos = gameState.getAgentPosition(self.index)
    currState = gameState.getAgentState(self.index)
    reward = 0.0


    # Get Enermy Index
    enermiesIndex = self.getOpponents(gameState)
    enemiesDistance = []
    minEnemiesDistance = 999
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
      for location in enermies:
        enemiesDistance.append(self.getMazeDistance(myPos,location))
      minEnemiesDistance = min(enemiesDistance)

    # Pacman will be eaten, Punish! That is very serious!
    if myPos == self.start and currState.isPacman:
      reward = reward - 20
    elif myState.isPacman and minEnemiesDistance == 1:
      reward = reward - 20

    # Eat food give one small reward
    if myState.numCarrying == currState.numCarrying + 1:
      reward = reward + 5

    



    else:
      # Closer to food, higher reward
      foodList = self.getFood(successor).asList()  

      foodList1 = self.getFood(gameState).asList()    
      if not len(foodList) == 0 and  not len(foodList1) == 0:
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        minDistance1 = min([self.getMazeDistance(currPos, food) for food in foodList1])

        if minDistance < minDistance1:
          reward += 1.0
        else:
          reward -= 1.0

    # Eat super food give one larger reward
    # Get capsule location after taking this action
    nowCapsule = self.getCapsules(successor)
    # Capsule is already eaten
    if not self.getCapsules(gameState) == []:
      # Capsule will be eaten in this step
      if len(nowCapsule) < len(self.getCapsules(gameState)):
        reward = reward + 40


    distanceToHome = self.getMazeDistance(myPos, self.start)
    distanceToHome1 = self.getMazeDistance(currPos, self.start)
    if distanceToHome < distanceToHome1 and currState.numCarrying >= 4:
      reward += 3.0


    



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

    print "reward: ", reward
    print "maxValue: ", maxValue
    print "difference: ", difference
    print "weights Before: ", weights
    print "features Before: ", features
    print "result Before: ", qValve


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









class DefensiveReflexAgent(MixAgent):
  
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

        if self.red:
            self.midWidth = (gameState.data.layout.width -1) / 2
        else:
            self.midWidth = ((gameState.data.layout.width - 1) / 2) + 1
        self.midHeight = gameState.data.layout.height / 2
        midPos = (self.midWidth,self.midHeight)
        myPos = gameState.getAgentPosition(self.index)

        """
        FIX NEED TO CHANGE
        """
        walls = gameState.getWalls().asList()
        temp = 1
        while midPos in walls:
          midPos = (self.midWidth,self.midHeight + temp)
          temp += 1


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
