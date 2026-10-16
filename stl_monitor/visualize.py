'''
1. visualization of STL robustness
2. input: robustness_table.csv
3. output:
      plots/<formula_name.png>
'''


import pandas as pd
import matplotlib.pyplot as plt
import os



class RobustnessVisualizer:


    def __init__(
        self,
        input_file="stl_monitor/robustness_table.csv",
        output_dir="plots/robustness"
    ):

        self.input_file = input_file
        self.output_dir = output_dir

        self.data = None



    #--------------------------------Load the robustness table--------------------------------------

    def load_data(self):

        self.data = pd.read_csv(
            self.input_file
        )



    #--------------------------------create output directory--------------------------------------

    def create_directory(self):

        if not os.path.exists(
            self.output_dir
        ):

            os.makedirs(
                self.output_dir
            )



    #--------------------------------plot a robustness signal--------------------------------------

    def plot_formula(
        self,
        formula_name
    ):


        time = self.data["time"]

        robustness = self.data[formula_name]



        plt.figure(
            figsize=(8,4)
        )


        plt.plot(
            time,
            robustness,
            label=formula_name
        )


        # violation boundary
        plt.axhline(
            y=0,
            linestyle="--",
            label="zero robustness"
        )


        plt.xlabel(
            "Time"
        )


        plt.ylabel(
            "Robustness"
        )


        plt.title(
            formula_name
        )


        plt.grid(
            True
        )


        plt.legend()



        filename = os.path.join(

            self.output_dir,

            formula_name + ".png"

        )


        plt.savefig(

            filename,

            bbox_inches="tight"

        )


        plt.close()



        print(
            "Saved:",
            filename
        )



    #--------------------------------plot formulas--------------------------------------

    def plot_robustness(self):


        columns = list(
            self.data.columns
        )


        # Remove timestamp

        formulas = [

            column

            for column in columns

            if column != "time"

        ]



        for formula in formulas:

            self.plot_formula(
                formula
            )



    #--------------------------------complete execution-------------------------------------

    def run(self):


        print(
            "\n--- Robustness Visualization ---"
        )


        self.load_data()


        self.create_directory()


        self.plot_robustness()


        print(
            "--------------------------------\n"
        )




#--------------------------------stabdalone execution--------------------------------------
if __name__ == "__main__":


    visualizer = RobustnessVisualizer()

    visualizer.run()
