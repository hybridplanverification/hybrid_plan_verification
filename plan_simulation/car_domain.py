'''
 1. car Domain based on PDDL+ definition
 2. Domain Specific
 3. Follows code constructs of "hybrid-automaton.py"
'''

from hybrid_automaton import (
    State,
    Action,
    Process,
    Event,
    HybridAutomaton,
)


#initial State

initial_state = State(
    time=0.0,

    # Location of hybrid automata
    location="RUNNING",

    values={

        "displacement": 0.0,

        "velocity": 0.0,

        "acceleration": 0.0,

        "running_time": 0.0,


        # predicate variables

        "running": True,

        "goal": False,

        "engine_blown": False,


        # constants

        "up_limit": 1.0,

        "down_limit": -1.0,
    },
)


automaton = HybridAutomaton(
    initial_state
)


#---------------------------Actions------------------------------

#---------------------------1.Accelerate---------------------------

#precondition of accelerate action
def can_accelerate(state):

    return (

        state.values["running"]

        and

        state.values["acceleration"]
        <
        state.values["up_limit"]

    )


#Effect of Accelerate action
def accelerate(state):

    state.values["acceleration"] += 1



automaton.add_action(
    Action(
        name="accelerate",

        condition=can_accelerate,

        effect=accelerate,
    )
)



#---------------------------2.Decelerate---------------------------

# Precondition of Decelerate action
def can_decelerate(state):

    return (

        state.values["running"]

        and

        state.values["acceleration"]
        >
        state.values["down_limit"]

    )


#Effect of Decelerate action
def decelerate(state):

    state.values["acceleration"] -= 1



automaton.add_action(
    Action(
        name="decelerate",

        condition=can_decelerate,

        effect=decelerate,
    )
)

#---------------------------3.Stop---------------------------

#Precondition of Stop action
def can_stop(state):
    
    EPS = 1e-6
    return (

        state.values["running"]
        
        and
        
        state.values["engine_blown"] == False

        and

        abs(state.values["velocity"]) <= EPS

        and

        state.values["displacement"] >= 30 - EPS

    )


#Effect of Stop action
def stop(state):

    print("STOP EFFECT EXECUTED")
    state.values["goal"] = True

    state.values["running"] = False

    state.location = "GOAL"



automaton.add_action(
    Action(
        name="stop",

        condition=can_stop,

        effect=stop,
    )
)


#---------------------------Process---------------------------

#precondition of Moving Process
def moving_enabled(state):

    return state.values["running"]


#Effect of Moving process
def moving_flow(state):


    return {

        "displacement":
            state.values["velocity"],


        "velocity":
            state.values["acceleration"],


        "running_time":
            1.0,

    }



automaton.add_process(
    Process(

        name="moving",

        condition=moving_enabled,

        derivatives=moving_flow,

    )
)


#---------------------------Engine_Explode Event------------------

#precondition of Engine_Explode event
def engine_explosion_enabled(state):
    EPS = 1e-6
    return (

        state.values["running"]

        and

        state.values["acceleration"] >= 1

        and

        state.values["velocity"] >= 100 - EPS

    )


#Efefct of Engine_Explode event
def engine_explosion(state):


    state.values["running"] = False

    state.values["engine_blown"] = True

    state.location = "FAILED"



automaton.add_event(
    Event(

        name="engine_explosion",

        condition=engine_explosion_enabled,

        effect=engine_explosion,

    )
)



#---------------------------Locations of hybrid automaton---------------------------

automaton.locations = [

    "RUNNING",

    "GOAL",

    "FAILED",

]



#---------------------------Build Car hybrid system---------------------------
def build_car_automaton():

    return automaton
