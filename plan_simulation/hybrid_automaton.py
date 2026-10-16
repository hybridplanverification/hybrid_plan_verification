from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


#---------------------------State of hybrid automata--------------------------- 

@dataclass
class State:
    '''
     1. Generic State Class of the hybrid automata
     2. Stores the state variables in dictionary
    '''

    time: float
    location: str
    values: Dict[str, Any]

    def copy(self):
        return State(
            time=self.time,
            location=self.location,
            values=self.values.copy()
        )


#---------------------------Action class---------------------------

@dataclass
class Action:
    '''
     1. Generic Action class
     2. name: name of the action
     3. condition: function checks the actiona applicable
     4. effect: function performs the disccre action update
    '''

    name: str
    condition: Callable[[State], bool]
    effect: Callable[[State], None]


#---------------------------Process class---------------------------

@dataclass
class Process:
    '''
    1. generic Process class
    2. name: name of the process of the domain
    3. condition: function checks the precondition of the process
    4. derivatives: returns the derivatives of the continuous variables
    '''

    name: str
    condition: Callable[[State], bool]
    derivatives: Callable[[State], Dict[str, float]]


#---------------------------Event class---------------------------

@dataclass
class Event:
    '''
    1. generic autonomous event class
    2. name: name of the pddl+ event
    3. condition: function checks whether the event is enabled or not
    4. effect: function updates the event's discrete action update
    '''

    name: str
    condition: Callable[[State], bool]
    effect: Callable[[State], None]


#---------------------------Hybrid Automaton class---------------------------

@dataclass
class HybridAutomaton:
    '''
    Generic Hybrid automaton class based on PDDL+ domains
    '''

    initial_state: State

    actions: Dict[str, Action] = field(default_factory=dict)

    processes: List[Process] = field(default_factory=list)

    events: List[Event] = field(default_factory=list)


    #---------------------------Actions---------------------------
    def add_action(self, action: Action):
        self.actions[action.name.lower()] = action


    def get_action(self, name: str):
        return self.actions.get(name.lower())


    #---------------------------processes---------------------------

    def add_process(self, process: Process):
        self.processes.append(process)


    #---------------------------events---------------------------

    def add_event(self, event: Event):
        self.events.append(event)


    #---------------------------Initial state---------------------------

    def get_initial_state(self):
        return self.initial_state.copy()
