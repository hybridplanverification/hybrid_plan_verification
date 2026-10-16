'''
STL monitoring framework:
 trace.csv -> trace preprocessor -> trace_monitor.csv -> stl monitor -> robustness_table.csv -> robustness visualizer -> plots
'''



from trace_preprocessor import TracePreprocessor
from stl_monitor import STLMonitor
from visualize import RobustnessVisualizer



def main():


    print(
        "\n-----------------------------------------"
    )

    print(
        " STL Monitoring Framework"
    )

    print(
        "------------------------------------------\n"
    )


    #----------------------------convert simulator trace into monitor trace------------------------

    preprocessor = TracePreprocessor(
       
        dt = 0.01,

        input_file="stl_monitor/trace.csv",

        output_file="stl_monitor/trace_monitor.csv",
        
        

    )


    preprocessor.run()



   #----------------------------evaluate stl formulas------------------------

    monitor = STLMonitor(

        trace_file="stl_monitor/trace_monitor.csv",

        formula_file="stl_monitor/formulas.txt",

        output_file="stl_monitor/robustness_table.csv"

    )


    monitor.run()



    #----------------------------plot robustness values------------------------

    visualizer = RobustnessVisualizer(

        input_file="stl_monitor/robustness_table.csv",

        output_dir="plots/robustness"

    )


    visualizer.run()



    print(
        "STL monitoring completed successfully."
    )



if __name__ == "__main__":

    main()
