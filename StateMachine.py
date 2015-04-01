#!/usr/bin/env python
import time
import re
#------------------------------------------------------------------------------
def sid():
  if not hasattr(sid, "counter"):
     sid.counter = 0
  sid.counter += 1
  return sid.counter
#------------------------------------------------------------------------------
class State(object):

    def __init__(self, sid, name):
        self.id = sid()
        self.name = name.upper()
        self.handlers = []
        self.input = lambda:None
        self.transitions = { None:self }
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def addHandler(self, handler, args = []):
        self.handlers.append( handler )
        return self
    def readInput(self):
        return self.input()
    def inputCallback(self, value):
        self.input = value
        return self
    def addTransition(self, condition, state):
        self.transitions.update( {condition:state} )
        return self
    def addTransitions(self, transitionsDict):
        for condition, state in transitionsDict.iteritems():
            self.addTransition(condition, state)
    def transition(self, sInput):
        try:
            state = self.transitions[sInput]
        except KeyError:
            state = self.transitions[None]
        finally:
            #print '[<{0:d}>{1:s}] ---> [<{2:d}>{3:s}]'.format( self.getID(), self.getName(), state.getID(), state.getName() )
            pass
        return state
#------------------------------------------------------------------------------
class StateMachine(object):

    def __init__(self, name):
        self.name = name.upper()
        self.states = []
        self.vars = {}
        self.fnc = {}
        self.tfnc = {}
        self.input = raw_input
        self._initial = None
        self._final = None
        self._current = None
    def addVar(self, name, value):
        self.vars.update( { name:value } )
    def addFunction(self, state, fnc, **kwargs):
        if state not in self.fnc:
            self.fnc.update( { state : {} } )
        self.fnc[state].update( { fnc.__name__: [ fnc, kwargs ] }  )
    def addTransitionFunction(self, state, fnc, **kwargs):
        if state not in self.tfnc:
            self.tfnc.update( { state : {} } )
        self.tfnc[state].update( { fnc.__name__: [ fnc, kwargs ] }  )
    def getStateMachineFunctions(self):
        return self.fnc
    def getStateFunctions(self, state):
        return self.fnc[state]
    def runFunction(self, state, fnc):
        f = self.fnc[state][fnc][0]
        kwargs = self.fnc[state][fnc][1]
        return f(self, kwargs)
    def runTransitionFunction(self, state, fnc):
        f = self.tfnc[state][fnc][0]
        kwargs = self.tfnc[state][fnc][1]
        return f(self, kwargs)
    def initial(self, state):
        self._initial = state
        self._current = self._initial
        return self
    def final(self, state):
        self._final = state
        return self
    def addStates(self, states):
        for state in states:
            self.states.append(state)
        return self
    def addTransitions(self, transitionsMatrix):
        for cstate, transitionsDict in transitionsMatrix.iteritems():
            for condition, nstate in transitionsDict.iteritems():
                cstate.addTransition(condition, nstate)
    def run(self, period=0, keyboardPaced=False):

        fo = kin = sInput = None
        
        while self._current is not self._final:
            
            self._current = self._current.transition( str( sInput) )
            
            for handler in self._current.handlers:
                handler()
            
            if self._current in self.getStateMachineFunctions():
                for fnc in self.getStateFunctions(self._current):
                    fo = self.runFunction(self._current, fnc)

            kin = self._current.readInput()
            
            if fo is not None:
                sInput = fo
            elif kin is not None:
                sInput = kin
            else:
                sInput = self.input("Input> ")
            if keyboardPaced:    
                self.input("Anykey> ")
            time.sleep(period)
#-HELPER-FUNCTIONS-------------------------------------------------------------
nx   = lambda  :   1
nop  = lambda x:   x
pp   = lambda x:   x+1
mm   = lambda x:   x-1
d2   = lambda x:   x/2
dn   = lambda x,n: x/n
gt   = lambda x,y: x>y
lt   = lambda x,y: x<y
gte  = lambda x,y: x>=y
lte  = lambda x,y: x<=y
#------------------------------------------------------------------------------
def printf(sm, kwargs):
    var = kwargs['var']
    print "DEBUG> {0:s} = {1:d}".format(var, sm.vars[var])

def vset(sm, kwargs):
    var = kwargs['var']
    value = kwargs['value']
    sm.vars[var] = value

def vget(sm, kwargs):
    var = kwargs['var']
    return sm.vars[var]

def save(sm, args):
    sname = args[0]
    dname = args[1]
    print "set = {0:d}".format(value)
    sm.vars[dname] = sm.vars[sname]

def transform(sm, kwargs):
    var = kwargs['var']
    f   = kwargs['f']
    sm.vars[var] = f( sm.vars[var] )

def transformAndSave(sm, kwargs):
    sname = kwargs['svar']
    dname = kwargs['dvar']
    f = kwargs['f']
    sm.vars[dname] = f( sm.vars[sname] )

def execute(sm, kwargs): #execute an external function with an internal variable
    f = kwargs['f']
    var = kwargs['var']
    arg = sm.vars[var]
    f(arg)
    return 1

def executeAndSave(sm, kwargs): #execute an external function with an and save result to an internal variable
    f = kwargs['f']
    dvar = kwargs['dvar']
    sm.vars[dvar] = f()
    return 1
# f()
# f(arg)
# ivar = f()
# f( ivar )
# ivar = f(ivar)
# transition conditions -> functions
#-EXTERNAL-FUNCTIONS----------------------------------------------------------
# def isHome():
#     print "Reading input...."
#     time.sleep(0.3)
#     #return '0'

# def moveByOne():
#     print "MoveByOne..."

# def move(steps):
#     print "MoveBy {0:d}...".format( int(steps) )
#     return 1

# def getAngle():
#     return 120.1

def recordAngle(angle):
    rfd = open('/home/config/options.cfg')
    data = rfd.read()
    wfd = open('/home/config/options.cfg', 'w')
    wfd.write( re.sub('/av_motor/zero_angle = [0-9\.]{1,}', '/av_motor/zero_angle = ' + str(angle), data) )
    rfd.close()
    wfd.close()
    print 'Zero Angle = {0:f} written to /home/config/options.cfg\r\n'.format(angle)
#------------------------------------------------------------------------------
def AutoZeroAvMotor(**external):

    isHome    = external['p1']
    moveByOne = external['p2']
    moveBy    = external['p3']
    getAngle  = external['p4']
    #debug     = external['debug']

    s0 = State(0, "Check for home on Startup").addHandler(moveByOne).inputCallback(isHome)
    s1 = State(1, "Move until home is found").addHandler(moveByOne).inputCallback(isHome)
    s2 = State(2, "Find where home ends, save counts").addHandler(moveByOne).inputCallback(isHome)
    s3 = State(3, "Save 1/2 counts.").inputCallback(nx)
    s4 = State(4, "Move until home is found again, the long way").addHandler(moveByOne).inputCallback(isHome)
    s5 = State(5, "Move half way of home to end of home")
    s6 = State(6, "Get angle and record angle")

    sm = StateMachine("Find and Record Home Position")

    sm.addVar('countStepsHomeRegion', 0)
    sm.addVar('halfWay', 0)
    sm.addVar('zero', 0)
    
    sm.addFunction(s0, vset,              var ='countStepsHomeRegion', value=0)
    
    sm.addFunction(s2, transform,         var ='countStepsHomeRegion', f=pp)
    #sm.addFunction(s2, printf,            var ='countStepsHomeRegion')
    
    sm.addFunction(s3, transformAndSave,  svar='countStepsHomeRegion', dvar ='halfWay', f=d2)
    #sm.addFunction(s3, printf,            var ='countStepsHomeRegion')
    #sm.addFunction(s3, printf,            var ='halfWay')
    
    sm.addFunction(s5, execute,             f = moveBy,      var = 'halfWay')

    sm.addFunction(s6, executeAndSave,      f = getAngle,   dvar = 'zero')
    sm.addFunction(s6, execute,             f = recordAngle, var = 'zero')

    sm.initial(s0).final(s6).addStates([s0, s1, s2, s3, s4, s5, s6])

    sm.addTransitions({  s0: {'x':s0, '1':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'x':s6},
                         s1: {'x':s0, 'x':s1, '0':s2, 'x':s3,'x':s4,'x':s5,'x':s6},
                         s2: {'x':s0, 'x':s1, 'x':s2, '1':s3,'x':s4,'x':s5,'x':s6},
                         s3: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'1':s4,'x':s5,'x':s6},
                         s4: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'0':s5,'x':s6},
                         s5: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'1':s6},
                         s6: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'x':s6} })
    try:
        sm.run(period = 0.0, keyboardPaced=False)
    except KeyboardInterrupt:
        print ""
#------------------------------------------------------------------------------
if __name__ == '__main__':

    # handlers function that doesn't take args nor returns 

    s0 = State(sid, "STATE0").addHandler(moveByOne).inputCallback(isHome)
    s1 = State(sid, "STATE1").addHandler(moveByOne).inputCallback(isHome)
    s2 = State(sid, "STATE2").addHandler(moveByOne).inputCallback(isHome)
    s3 = State(sid, "STATE3").inputCallback(nx)
    s4 = State(sid, "STATE4").addHandler(moveByOne).inputCallback(isHome)
    s5 = State(sid, "STATE5")
    s6 = State(sid, "STATE6").addHandler(recordAngle)

    sm = StateMachine("Find and Record Home Position")

    sm.addVar('countStepsHomeRegion', 0)
    sm.addVar('halfWay', 0)
    sm.addVar('zero', 0)
    
    sm.addFunction(s0, fset,              var ='countStepsHomeRegion', value=0)
    
    sm.addFunction(s2, transform,         var ='countStepsHomeRegion', f=pp)
    sm.addFunction(s2, printf,            var ='countStepsHomeRegion')
    
    sm.addFunction(s3, transformAndSave,  svar='countStepsHomeRegion', dvar ='halfWay', f=d2)
    sm.addFunction(s3, printf,            var ='countStepsHomeRegion')
    sm.addFunction(s3, printf,            var ='halfWay')
    
    sm.addFunction(s5, execute,             f = move, var = 'halfWay')
    sm.addFunction(s6, executeAndSave,      f = getAngle, dvar = 'zero')

    sm.initial(s0).final(s6).addStates([s0, s1, s2, s3, s4, s5, s6])

    sm.addTransitions({ s0: {'x':s0, '0':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'x':s6},
                        s1: {'x':s0, 'x':s1, '1':s2, 'x':s3,'x':s4,'x':s5,'x':s6},
                        s2: {'x':s0, 'x':s1, 'x':s2, '0':s3,'x':s4,'x':s5,'x':s6},
                        s3: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'1':s4,'x':s5,'x':s6},
                        s4: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'1':s5,'x':s6},
                        s5: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'1':s6},
                        s6: {'x':s0, 'x':s1, 'x':s2, 'x':s3,'x':s4,'x':s5,'x':s6} })
    try:
        sm.run(period = 0.5, keyboardPaced=True)
    except KeyboardInterrupt:
        print ""
#------------------------------------------------------------------------------

