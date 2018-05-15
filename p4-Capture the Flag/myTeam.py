from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
			   first = 'OffensiveAgent', second = 'DefensiveAgent'):
    
	return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class AlphaBetaAgent(CaptureAgent):

	# init state with start state, mid postion, timer, close to food center
	def registerInitialState(self, gameState):
        
		CaptureAgent.registerInitialState(self, gameState)
		self.start = gameState.getAgentPosition(self.index)
		self.closestFoodToCenter = None
		self.timer = 0

		# mid positon and aviod wall
		midHt = gameState.data.layout.height/2
		midWh = gameState.data.layout.width/2
        
		while(gameState.hasWall(midWh, midHt)):

			midHt -= 1
			if midHt == 0:
				midHt = gameState.data.layout.height
		self.midPos = (midWh, midHt)

		# two agents
		agentsTeam = []
		agentsLen = gameState.getNumAgents()
		i = self.index
		while len(agentsTeam) < (agentsLen/2):

			agentsTeam.append(i)
			i += 2
			if i >= agentsLen:

				i = 0
		agentsTeam.sort()
		self.registerTeam(agentsTeam)


	# Alphabeta algorithm for agents
	def alphabeta(self, gameState, agent, mdepth, alpha, beta,visibleAgents):

		# reset number
		if agent >= gameState.getNumAgents():

			agent = 0

		# add depth
		if agent == self.index:

			mdepth += 1

		# chech if visiblaAgents
		if agent not in visibleAgents:

			return self.alphabeta(gameState, agent + 1, mdepth, alpha, beta, visibleAgents)

		# check depth or game over
		if mdepth == 1 or gameState.isOver():

			if agent == self.index:

				return self.evaluate(gameState)

			else:

				self.alphabeta(gameState, agent + 1, mdepth, alpha, beta, visibleAgents)

        # agents action
		legalActions = gameState.getLegalActions(agent)
		if agent in self.agentsOnTeam:

			v = float("-inf")
			for action in legalActions:

				v = max(v, self.alphabeta(gameState.generateSuccessor(agent, action), agent + 1,mdepth, alpha, beta, visibleAgents))
				if v > beta:
					return v
				alpha = max(alpha, v)
			return v
		else:
			v = float("inf")
			for action in legalActions:
				v = min(v, self.alphabeta(gameState.generateSuccessor(agent, action), agent + 1,mdepth, alpha, beta, visibleAgents))
				if v < alpha:
					return v
				beta = min(beta, v)
			return v

	def getFeatures(self, gameState):
		"""
		Returns a counter of features for the state
		"""
		features = util.Counter()
		features['successorScore'] = self.getScore(gameState)
		return features


	def getWeights(self, gameState):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0}


	def evaluate(self, gameState):
		"""
		Computes a linear combination of features and feature weights
		"""
		features = self.getFeatures(gameState)
		weights = self.getWeights(gameState)
		return features * weights

class OffensiveAgent(AlphaBetaAgent):

	def chooseAction(self, gameState):
		start = time.time()

        # all visible agents
		allAgents = range(0, gameState.getNumAgents())
		visibleAgents = [a for a in allAgents if gameState.getAgentState(a).getPosition() is not None]

		# alphaBete method

		v = (float("-inf"), 'None')
		alpha = float('-inf')
		beta = float('inf')
		legalActions = gameState.getLegalActions(self.index)
		for action in legalActions:

			if action == 'Stop':
				continue
			v = max(v, (self.alphabeta(gameState.generateSuccessor(self.index, action), self.index+1, 0, alpha, beta, visibleAgents), action))
			if v[0] > beta:
				return v[1]
			alpha = max(alpha, v[0])
		return v[1]

	def getFeatures(self, gameState):
		features = util.Counter()
		foodList = self.getFood(gameState).asList()
		#postive score for red , negative score for blue
		if self.red:
			features['successorScore'] = gameState.getScore()
		else:
			features['successorScore'] = -1* gameState.getScore()

		features['successorScore'] -= len(foodList)
		features['distanceToGhost'] = 0

		allAgents = range(0, gameState.getNumAgents())
		visibleAgents = [a for a in allAgents if gameState.getAgentState(a).getPosition() != None]

		currPos = gameState.getAgentState(self.index).getPosition()

       #if enemy is visable
		if not set(visibleAgents).isdisjoint(self.getOpponents(gameState)):

			# Agent stay away from ghost if agent is pacman or scared.
			if gameState.getAgentState(self.index).isPacman and gameState.getAgentState(self.index).scaredTimer > 0:

				ghosts = list(set(visibleAgents).intersection(self.getOpponents(gameState)))

				for ghost in ghosts:
					ghostPos = gameState.getAgentState(ghost).getPosition()
					dist = self.getMazeDistance(currPos, ghostPos)
					# keep 2 distance.
					if dist <= 2:
						features['distanceToGhost'] = -9999
					else:
						features['distanceToGhost'] += 0.5 * dist

			# try to stay away from ghost
			else:
				ghosts = list(set(visibleAgents).intersection(self.getOpponents(gameState)))

				for ghost in ghosts:

					ghostPos = gameState.getAgentState(ghost).getPosition()
					dist = self.getMazeDistance(currPos, ghostPos)

					features['distanceToGhost'] += 0.5 * dist

		# if emeny are not  visable
		else:
			ghosts = list(set(allAgents).difference(self.agentsOnTeam))
			for ghost in ghosts:
				ghostDists = gameState.getAgentDistances()
				features['distanceToGhost'] += ghostDists[ghost]

		# Agent take fodd util has 6 foods
		if gameState.getAgentState(self.index).numCarrying < 6:

			myPos = gameState.getAgentState(self.index).getPosition()

			if len(foodList) > 0:
				minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
				features['distanceToFood'] = minDistance
			else:
				myPos = gameState.getAgentState(self.index).getPosition()
				features['distanceToFood'] = self.getMazeDistance(myPos, self.start)
		else:
			myPos = gameState.getAgentState(self.index).getPosition()
			features['distanceToFood'] = self.getMazeDistance(myPos, self.start)
		return features

	def getWeights(self, gameState):
		return {'successorScore': 100, 'distanceToFood': -1, 'distanceToGhost': 1}

class DefensiveAgent(AlphaBetaAgent):

	def chooseAction(self, gameState):
		start = time.time()

		# all visible agents
		allAgents = range(0, gameState.getNumAgents())
		visibleAgents = [a for a in allAgents if gameState.getAgentState(a).getPosition() is not None]

		#alphaBete method
		v = (float("-inf"), 'None')
		alpha = float('-inf')
		beta = float('inf')
		legalActions = gameState.getLegalActions(self.index)
		for action in legalActions:
			if action == 'Stop':
				continue
			v = max(v, (self.alphabeta(gameState.generateSuccessor(self.index, action), self.index+1, 0, alpha, beta, visibleAgents), action))
			if v[0] > beta:

				return v[1]
			alpha = max(alpha, v[0])

		#  timer for the patrol function.
		self.timer -= 1

		return v[1]

	def getFeatures(self, gameState):
		features = util.Counter()
		myState = gameState.getAgentState(self.index)
		myPos = myState.getPosition()
		foodList = self.getFoodYouAreDefending(gameState).asList()

		# get distance to invaders
		enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
		invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
		features['numInvaders'] = len(invaders)

		# check enemies
		if len(invaders) > 0:
			dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
			features['invaderDistance'] = max(dists)
		else:
			#around mid position if not found enemy
			if self.closestFoodToCenter:
				dist = self.getMazeDistance(myPos, self.closestFoodToCenter)
			else:
				dist = None

			# find nearby food
			if self.timer == 0 or dist == 0:
				self.timer = 20
				foods = []
				for food in foodList:
					foods.append((self.getMazeDistance(self.midPos, food), food))
				foods.sort()
				chosenFood = random.choice(foods[:3])
				self.closestFoodToCenter = chosenFood[1]
			dist = self.getMazeDistance(myPos, self.closestFoodToCenter)
			features['invaderDistance'] = dist
		return features

	def getWeights(self, gameState):
		return {'numInvaders': -1000, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}