'''
plot the trace.csv generated after simulation
plot Boolean, discrete, continuous variables along with actions timeline

'''

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "plots", "tace")
os.makedirs(path, exist_ok=True)

class TracePlotter:


    def __init__(self, filename):

        self.filename = filename

        self.data = pd.read_csv(
            filename
        

        )


    #-----------------------plot continuous variables--------------------------
    def plot_continuous(self):

        time = self.data["time"]


        ignore = [

            "time"

        ]


        numeric_columns = (

            self.data
            .select_dtypes(
                include=["float64", "int64"]
            )
            .columns
        )


        for signal in numeric_columns:


            if signal in ignore:

                continue


            plt.figure(
                figsize=(8, 4)
            )


            plt.plot(

                time,

                self.data[signal]

            )


            plt.xlabel(
                "Time"
            )


            plt.ylabel(
                signal
            )


            plt.title(
                signal
            )


            plt.grid(
                True
            )


            plt.tight_layout()


            plt.savefig(os.path.join(path, signal + ".png"))


            plt.close()



    #-----------------------plot boolean variables--------------------------

    def plot_boolean(self):

        time = self.data["time"]


        boolean_columns = (

            self.data
            .select_dtypes(
                include=["bool"]
            )
            .columns
        )


        if len(boolean_columns) == 0:

            return



        plt.figure(
            figsize=(8,4)
        )


        for signal in boolean_columns:


            plt.step(

                time,

                self.data[signal],

                where="post",

                label=signal

            )


        plt.xlabel(
            "Time"
        )


        plt.ylabel(
            "Value"
        )


        plt.title(
            "Boolean Predicates"
        )


        plt.legend()


        plt.grid(
            True
        )


        plt.tight_layout()



        plt.savefig(os.path.join(path, "predicates.png"))

        plt.close()



    #-----------------------plot discrete locations--------------------------

    def plot_locations(self):


        if "location" not in self.data.columns:

            return



        time = self.data["time"]



        locations = (

            self.data["location"]
            .astype("category")

        )


        location_values = (

            locations
            .cat.codes

        )



        plt.figure(
            figsize=(8,4)
        )


        plt.step(

            time,

            location_values,

            where="post"

        )


        plt.yticks(

            range(
                len(
                    locations.cat.categories
                )
            ),

            locations.cat.categories

        )


        plt.xlabel(
            "Time"
        )


        plt.ylabel(
            "Location"
        )


        plt.title(
            "Hybrid Automaton Location"
        )


        plt.grid(
            True
        )


        plt.tight_layout()



        plt.savefig(os.path.join(path, "locations.png"))

        plt.close()



    #-----------------------plot discrete actions--------------------------

    def plot_actions(self):


        if "action" not in self.data.columns:

            return



        actions = self.data[

            self.data["action"].notna()

            &

            (self.data["action"] != "")

        ]



        if len(actions) == 0:

            return



        plt.figure(
            figsize=(8,3)
        )


        for _, row in actions.iterrows():


            plt.axvline(

                row["time"]

            )


            plt.text(

                row["time"],

                0,

                row["action"],

                rotation=90

            )



        plt.xlabel(
            "Time"
        )


        plt.title(
            "Discrete Actions"
        )


        plt.yticks([])


        plt.grid(
            True
        )


        plt.tight_layout()


        plt.savefig(os.path.join(path, "actions.png"))


        plt.close()



#-----------------------standalone execution--------------------------

if __name__ == "__main__":


    plotter = TracePlotter(
        "stl_monitor/trace.csv"
    )


    plotter.plot_continuous()

    plotter.plot_boolean()

    plotter.plot_locations()

    plotter.plot_actions()


    print(
        "Plots generated successfully"
    )
