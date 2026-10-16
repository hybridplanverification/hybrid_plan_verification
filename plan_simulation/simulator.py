
'''
------------------------------Hybrid automaton simulator------------------------------

supports PDDL+:
  1. processes
  2. actions
  3. events


Simulation:
    integration_dt = 0.0001 (continuous updates happens for every 0.0001 time units)

    trace recording_dt = 0.001 (updates store for every 0.001 time units)
    
    descrete action/events records immediately


'''

from copy import deepcopy

from enhsp_plan_parser import (
    WaitEvent,
    ActionEvent
)


#------------------------------External distrubance class------------------------------

class ExternalDisturbance:

    def __init__(
        self,
        start_time=0.0,
        end_time=float("inf"),
        acceleration=0.0
    ):

        self.start_time = start_time
        self.end_time = end_time
        self.acceleration = acceleration


    def get_disturbance(self, state):

        """
        Return external acceleration disturbance
        active at the current simulation time.
        """

        if (
            self.start_time
            <= state.time
            < self.end_time
        ):

            return self.acceleration

        return 0.0


#------------------------------Simulator class------------------------------

class Simulator:

    #constructor

    def __init__(
        self,
        automaton,
        plan,
        trace,
        integration_dt=0.0001,
        record_dt=0.01,
        disturbance=None
    ):

        self.automaton = automaton

        self.plan = plan

        self.trace = trace

        #------------------------------numerical integration step------------------------------

        self.integration_dt = integration_dt

        #------------------------------trace recording step------------------------------

        self.record_dt = record_dt

        self.disturbance = disturbance

        #------------------------------initial state------------------------------

        self.state = deepcopy(
            automaton.get_initial_state()
        )

        

        self.next_record_time = None


    #------------------------------simulate function------------------------------

    def simulate(self, Tmax):

        '''
         The parsed plan executes
         if the plan finishes before T_{max} then the system will stay in the same final state until the time elsapses.
        '''

        #------------------------------Execute the plan------------------------------

        for event in self.plan:

            if isinstance(event, WaitEvent):

                self.execute_wait(event)

            elif isinstance(event, ActionEvent):

                self.execute_action(event)


        
        current_time = self.state.time


         #------------------------------continue simulation after plan ends till the max time elapses------------------------------

        if current_time < Tmax - 1e-12:


            self.next_record_time = (
                current_time + self.record_dt
            )


            while current_time < Tmax - 1e-12:


                remaining_time = (
                    Tmax - current_time
                )

                step = min(
                    self.integration_dt,
                    remaining_time
                )

                self._current_dt = step


                self.integrate()


                current_time += step


                current_time = round(
                    current_time,
                    12
                )

                self.state.time = current_time


                self.execute_events()


                if (
                    current_time >=
                    self.next_record_time - 1e-10
                ):

                    self.record_state()



                    while (
                        self.next_record_time
                        <= current_time + 1e-10
                    ):

                        self.next_record_time += (
                            self.record_dt
                        )



            if (
                len(self.trace.rows) == 0
                or
                abs(
                    self.trace.rows[-1]["time"]
                    - Tmax
                ) > 1e-10
            ):

                self.state.time = Tmax

                self.record_state()


        return self.trace

 #------------------------------continuous evolution during wait period------------------------------

    def execute_wait(self, wait):

        current_time = wait.start

        self.state.time = current_time

        self.record_state()

        self.next_record_time = (
            current_time + self.record_dt
        )

        while current_time < wait.end - 1e-12:

            remaining_time = (
                wait.end - current_time
            )

            step = min(
                self.integration_dt,
                remaining_time
            )

            self._current_dt = step

            self.integrate()

            current_time += step

            current_time = round(
                current_time,
                12
            )

            self.state.time = current_time

            self.execute_events()

            if (
                current_time >=
                self.next_record_time - 1e-10
            ):

                self.record_state()

                while (
                    self.next_record_time
                    <= current_time + 1e-10
                ):

                    self.next_record_time += (
                        self.record_dt
                    )


        if (
            len(self.trace.rows) == 0
            or
            abs(
                self.trace.rows[-1]["time"]
                - wait.end
            ) > 1e-10
        ):

            self.state.time = wait.end

            self.record_state()



 #------------------------------Execute the planner action------------------------------

    def execute_action(self, action_event):

        

        action = self.automaton.get_action(
            action_event.name
        )


        if action is None:

            raise ValueError(
                f"Unknown action: {action_event.name}"
            )

        self.state.time = action_event.time

        # Action precondition check
        if action.condition(self.state):

            # action update
            action.effect(self.state)

        else:

            print(
                "Action not applicable:",
                action_event.name
            )
            
        # Action may enable the events
        self.execute_events()

        # record the state
        self.record_state(
            action=action_event.name
        )

 #------------------------------Euler Integration------------------------------

    def integrate(self):


        
        dt = getattr(
            self,
            "_current_dt",
            self.integration_dt
        )


        derivatives = {}


         #------------------------------evaluate all active processes------------------------------

        for process in self.automaton.processes:

             #------------------------------check process active?------------------------------

            if not process.condition(self.state):

                continue


             #------------------------------obtain process derivatives------------------------------

            flow = process.derivatives(
                self.state
            )


             #------------------------------combine derivatives------------------------------
             
            for variable, value in flow.items():

                if variable not in derivatives:

                    derivatives[variable] = 0.0

                derivatives[variable] += value


         #------------------------------External distrubance------------------------------
        if self.disturbance is not None:

            disturbance = (
                self.disturbance.get_disturbance(
                    self.state
                )
            )


            if disturbance != 0.0:

                if "velocity" not in derivatives:

                    derivatives["velocity"] = 0.0

                derivatives["velocity"] += disturbance


         #------------------------------Euler update------------------------------

        for variable, derivative in derivatives.items():

            self.state.values[variable] += (
                derivative * dt
            )


     #------------------------------Autonomous event updation------------------------------

    def execute_events(self):


        event_triggered = True


        while event_triggered:

            event_triggered = False


            for event in self.automaton.events:

                 #------------------------------check event condition------------------------------

                if event.condition(self.state):

                     #------------------------------apply event effect------------------------------
                    event.effect(self.state)


                     #------------------------------record transition immediately------------------------------
                    self.record_state(
                        action=event.name
                    )


                    event_triggered = True

                    break


     #------------------------------record trace------------------------------

    def record_state(
        self,
        action=""
    ):


        self.trace.record(
            time=self.state.time,
            action=action,
            state=self.state
        )


