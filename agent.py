# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 12:39:16 2023

@author: Jtiquet
"""
import random as rnd


class Agent():
    orderQueue = []
    states = []
    TreeLevel = []
    delta = {}
    heuristicTest = 0
    
    def __init__(self):
        
        self.remember()

    def isknowkn(self, state, options):
        isknown = False
        foundthis = ''
        for situation in self.states:
            situation = situation.strip().split('<')
            isSimilar = True
            known_objects = {"enemy": [], "pipe": [], "floor": [], "brick": []}

            for obj in situation:
                if not obj == '':
                    name, pos = obj.split(':')
                    if name in known_objects:
                        known_objects[name].append(pos)
                    else:
                        known_objects[name] = [pos]

            for widget in state:
                name = widget.__str__()
                pos = str(widget.pos)

                if pos not in known_objects[name]:
                    #print(name, pos,'List: ', known_objects[name])
                    isSimilar = False
                    break

            if isSimilar:
                foundthis = situation
                isknown = True
                break

        if isknown:
            #print('foundthis  ',foundthis)
            pass
        return isknown

    def memorize(self, data=''):
        file = open('.//AgentMemory.txt', 'a')
        file.write(data)
        file.close()

    def rewriteALL(self, data=None):

        file = open('.//AgentMemory.txt', 'w')
        if not data:
            everything = '#states\n'
            for state in self.states:
                everything += state

            everything += '#transitions\n'
            for delta in self.delta:
                everything += delta
        
        file.write(everything)
        file.close()

    def remember(self):
        self.states = []
        self.delta = {}
        self.heuristicTest = 0
        secciones = {"#states": [], "#transitions": []}
        # -- Look into file of data
        with open('.//AgentMemory.txt', 'r') as f:
            lines = f.readlines()
            seccion_actual = None
            for line in lines:
                line = line.strip()
                if line in secciones:
                    seccion_actual = line
                elif seccion_actual and line:
                    secciones[seccion_actual].append(line)
            f.close()

            # -- Organize info
            for line in secciones['#states']:
                self.states.append(line)

            for line in secciones['#transitions']:
                if line:
                    initialState, actionindex = line.split(':')
                    actionindex, nextState = actionindex.split('<')
                    if initialState not in self.delta:
                        self.delta[initialState] = [0,0,0,0]
                    self.delta[initialState][int(actionindex)] = nextState
            
        self.organizeStates()

    def sendStats(self, state):
        if not self.isknowkn(state, 'implement plz'):
            objects = ''
            for widget in state:
                objects += widget.__str__() + ':' + str(widget.pos) + '<'
                #objects += widget.__str__() + ':' + widget.pos + '<'
            self.memorize('#states\n' + objects[:-1] + '\n')
        else:
            print('YEAH WHAT A COINCIDENCE')

    def setStats(self, uniqueId, timer, options, heuristic, isalive = True):
        uniqueId = str(uniqueId)
        timer = str(timer)
        options = str(options)
        heuristic = str(heuristic)
        isalive = '1' if isalive else '0' 
        self.memorize('#states\n' + uniqueId +':'+ timer +':'+ options +':'+ heuristic +':'+ isalive + '\n')
        
    def setTransition(self, prevStatId, actionindex, nextStatId):
        prevStatId = str(prevStatId)
        actionindex = str(actionindex)
        nextStatId = str(nextStatId)
        self.memorize('#transitions\n' +prevStatId+':'+ actionindex +'<'+ nextStatId + '\n')
    
    def isSeted(self, Id):
        pass
    
    def getOrders(self):
        orders = self.orderQueue
        self.orderQueue = []
        print(self.orderQueue)
        return orders
    def getHeuristic(self, state=0):
        self.heuristicTest += 1
        return self.heuristicTest
    def organizeStates(self):
        self.info = {}
        maxtimer = 0
        maxheuristic = 0
        maxheuristicId = '0'
        for state in self.states:
            state = state.split(':')
            uniqueId = state[0]
            timer = int(state[1])
            options = state[2]
            heuristic = state[3]
            isalive = state[4]
            
            if maxtimer < timer:
                maxtimer = timer
                '''
            options = (options.replace('[','').replace(']','').replace(' ','').split(','))
            for i in range(len(options)):
                if options[i] == 'True':
                    options[i] = True
                elif options[i]== 'False':
                    options[i] = False
            # - Correcting stuff
            #self.states[state][2] = options
            '''
            options = []
            if uniqueId in self.delta:
                options = self.delta[uniqueId]
                        
            heuristic = float(heuristic)
            isalive = False if isalive == '0' else True  
            if maxheuristic < heuristic:
                maxheuristic = heuristic
                maxheuristicId = uniqueId
            self.info[uniqueId] = [timer, options, heuristic, isalive]

        # - self.TreeLevel = [[]]*(maxtimer+1)
        # - toca así para evitar un bug, este for se ve muy noob pero es por un bug extraño
        for i in range(maxtimer+1):
            self.TreeLevel.append([])
        for dataId in self.info:
            data = self.info[dataId]
            self.TreeLevel[int(data[0])].append(dataId)
        self.maxheuristicId = maxheuristicId
        self.lastdecision()
                
    def searchdecisions(self, ID):
        prevState = self.info[ID][0] - 1
        if prevState > 0:
            isfound = False
            for dataId in self.TreeLevel[prevState]:
                depuration = self.info[dataId][1]
                if ID in self.info[dataId][1]:
                    prevState = dataId
                    decisionIndex = self.info[dataId][1].index(ID)
                    self.orderQueue.append(decisionIndex)
                    isfound = True
                    break
            if isfound:
                self.searchdecisions(prevState)
            else:
                print('Reset')
        else:
            # This is not really mandatory but is implemented anyways
            return self.orderQueue

    def lastdecision(self):
        if not self.maxheuristicId == '0':
            self.searchdecisions(self.maxheuristicId)
            nextStep = self.info[self.maxheuristicId][1]
            #self.orderQueue.append(self.takedecision(nextStep))
    '''
    def takedecision(self, uuid, options):
        unexplored = []
        for actionindex in range(len(options)):
            if options[actionindex]:
                unexplored.append(actionindex)
        decision = rnd.randint(0, len(unexplored)-1) if not unexplored == [] else 3
        return decision
        #self.orderQueue.append(unexplored[decision])
    '''    
    def takedecision(self, uuid, options):
        unexplored = []
        # - add every action index that is true 
        # - previously formated with which actions are allowed in Mario collision filters
        for actionindex in range(len(options)):
            if options[actionindex]:
                unexplored.append(actionindex)
        
        # - now take a look if it already has been explored
        newpath = []
        knowknpath = []
        isnew = False
        for actionindex in unexplored:
            if uuid in self.delta: 
                isnew = False
                nextuuid = self.delta[uuid][actionindex]
                if nextuuid == 0 or nextuuid == '0':
                    newpath.append(actionindex)
                else:
                    knowknpath.append((actionindex,nextuuid))
            else:
                isnew = True
        # - There is some path unexplored in this decision _ prioritize them
        decision = 3
        if isnew:
            decision = unexplored[rnd.randint(0, len(unexplored)-1)]
            if 1 in unexplored:
                decision = 1 if rnd.randint(0, 1) == 1 else decision
        else:
            if not newpath == []:    
                # - here is random because none of these paths have heuristic yet
                decision = rnd.randint(0, len(newpath)-1)
            else:
                # - Here i need some filters about heuristic, try to explore the more convenient
                maxheuristic = 0
                for touple in knowknpath:
                    actionindex, nextuuid = touple  
                    if self.info[nextuuid][2] > maxheuristic:
                        maxheuristic = self.info[nextuuid][2]
                        decision = actionindex
            
        return decision