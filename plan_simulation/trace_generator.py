'''
generate sthe hybrid automaton trace 
create trace.scv file for further stl monitoring

'''

import pandas as pd



class TraceGenerator:


    def __init__(self):

        self.rows = []



     #------------------------------record simulator state------------------------------

    def record(
        self,
        time,
        state,
        action=""
    ):


        row = {}



         #------------------------------time------------------------------

        row["time"] = round(
            time,
            6
        )



        #------------------------------Discrete transition information------------------------------

        row["action"] = action



         #------------------------------hybrid automaton location------------------------------

        row["location"] = state.location



         #------------------------------Store all state variables ------------------------------

        for variable, value in state.values.items():


            # Do not store constants

            if variable in (
                "up_limit",
                "down_limit"
            ):

                continue



            row[variable] = value



        self.rows.append(row)



     #------------------------------convert trace to dataframe------------------------------

    def dataframe(self):

        return pd.DataFrame(
            self.rows
        )

    
    '''
     refine the trace by removing redundant samples or data
    '''

    def refine_trace(self):

        refined = []

        i = 0

        while i < len(self.rows):

            current = self.rows[i]


            if (
                i > 0
                and current["action"] == ""
                and self.rows[i - 1]["action"] != ""
                and current["time"] == self.rows[i - 1]["time"]
            ):
                i += 1
                continue

            refined.append(current.copy())

            i += 1


        self.rows = refined
        
    
      
    #------------------------------Save csv file------------------------------

    def save(self, filename):

        # Refine trace before exporting
        self.refine_trace()

        df = self.dataframe()

        df.to_csv(
            filename,
            index=False
        )

        print(
            f"Trace saved to {filename}"
        )
    
     #------------------------------print the trace------------------------------

    def print(self):

        print(
            self.dataframe()
        )
