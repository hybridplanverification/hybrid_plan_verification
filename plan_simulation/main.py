'''
1. Hybrid automata simulator framework
2. car domain -> Hybrid automaton -> ENHSP plan parser -> hybrid simulator -> trace generator -> trace.csv

'''


from car_domain import build_car_automaton

from enhsp_plan_parser import ENHSPPlanParser

from simulator import (
    Simulator,
    ExternalDisturbance
)

from trace_generator import TraceGenerator

from plot_results import TracePlotter


#------------------------------configuration details------------------------------

PLAN_FILE = "plan_simulation/plans/plan.txt"

TRACE_FILE = "stl_monitor/trace.csv"

TIME_STEP = 0.0001
T_MAX = 50


#------------------------------External distrubance------------------------------

DISTURBANCE_START = 8.0

DISTURBANCE_END = 20.0

DISTURBANCE_ACCELERATION = 10.0


#------------------------------driver function that enables the simulation------------------------------

def main():

    #------------------------------create hybrid automaton------------------------------

    automaton = build_car_automaton()


    #------------------------------parse ENHSP plan------------------------------

    parser = ENHSPPlanParser(
        PLAN_FILE
    )

    plan = parser.parse()

    print("\nParsed Plan")

    parser.print_events()

    #------------------------------create trace generator------------------------------
   
    trace = TraceGenerator()


   #------------------------------create external distrubance------------------------------

    disturbance = ExternalDisturbance(

        start_time=DISTURBANCE_START,

        end_time=DISTURBANCE_END,

        acceleration=DISTURBANCE_ACCELERATION

    )


    print("\nExternal Disturbance")

    print(
        f"Start time: {DISTURBANCE_START}"
    )

    print(
        f"End time: {DISTURBANCE_END}"
    )

    print(
        f"Acceleration: "
        f"{DISTURBANCE_ACCELERATION}"
    )


   #------------------------------create simulator------------------------------

    simulator = Simulator(

        automaton=automaton,

        plan=plan,

        trace=trace,

        #dt=TIME_STEP,

        #disturbance=disturbance
        disturbance=None

    )


    #------------------------------run simulator------------------------------

    simulator.simulate(T_MAX)
    #simulator.simulate()


    #------------------------------create trace------------------------------

    trace.save(
        TRACE_FILE
    )


    #------------------------------plot trace------------------------------

    plotter = TracePlotter(
        TRACE_FILE
    )

    plotter.plot_continuous()

    plotter.plot_boolean()

    plotter.plot_locations()

    plotter.plot_actions()


    
    print(
        "\nSimulation completed successfully"
    )

    print(
        f"Trace stored in {TRACE_FILE}"
    )


#------------------------------Initiation------------------------------

if __name__ == "__main__":

    main()
