'''
1. trace preprocesor for monitoring task
2. input: trace.scv
3. output: trace_monitor.csv
4. generated signals:
      Intial_state, action signals, constant parameters

'''

import pandas as pd


class TracePreprocessor:

    def __init__(
        self,
        dt,
        input_file="stl_monitor/trace.csv",
        output_file="stl_monitor/trace_monitor.csv"
    ):

        self.input_file = input_file
        self.output_file = output_file

        self.trace = None
        self.dt = dt

    #----------------------------add constant parameters------------------------
    def add_constant_parameters(self):

        self.trace["upLimit"] = 1

        self.trace["downLimit"] = -1

        self.trace["dt"] = self.dt

    
    #----------------------------Load trace------------------------

    def load_trace(self):

        self.trace = pd.read_csv(
            self.input_file
        )


        if "action" in self.trace.columns:

            self.trace["action"] = (
                self.trace["action"]
                .fillna("")
                .astype(str)
            )

    #----------------------------geenrate initial_state signal------------------------

    def generate_initial_signal(self):

        if "time" not in self.trace.columns:
            return

        self.trace["initial"] = (

            self.trace["time"] == 0

        )
      


    #----------------------------generate action predicates------------------------

    def generate_action_signals(self):

        if "action" not in self.trace.columns:
            return

        actions = (

            self.trace["action"]
            .unique()

        )

        for action in actions:

            # Ignore empty process steps

            if action == "":
                continue

            signal_name = (

                "action_"
                +
                str(action).lower()

            )

            self.trace[signal_name] = (

                self.trace["action"]
                ==
                action

            )

    #----------------------------generate process signal------------------------

    def generate_process_signal(self):

        if "action" not in self.trace.columns:
            return

        self.trace["process"] = (

            self.trace["action"] == ""

        )
    
    #----------------------------generate teminal signal------------------------

    def generate_terminal_signal(self):

        if "location" not in self.trace.columns:
            return

        location = (
            self.trace["location"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        self.trace["terminal"] = (
            location.isin(["GOAL", "FAILED"])
        ).astype(int)
    
    
    #----------------------------save output trace------------------------

    def save(self):

        self.trace.to_csv(

            self.output_file,

            index=False

        )

        print(
            f"Generated: {self.output_file}"
        )

    #----------------------------complete pipeline------------------------

    def run(self):

        print("\n--- Trace Preprocessing ---")

        print("Loading trace")

        self.load_trace()

        print("Generating initial-state signal")

        self.generate_initial_signal()


        print("Generating action signals")

        self.generate_action_signals()


        print("Adding constant parameters")

        self.add_constant_parameters()

        print("Generating process signal")

        self.generate_process_signal()
        
        self.generate_terminal_signal()

        print("Saving monitoring trace")

        self.save()

        print("---------------------------\n")


#----------------------------standalone execution------------------------

if __name__ == "__main__":

    preprocessor = TracePreprocessor(
        dt=0.01
    )

    preprocessor.run()

