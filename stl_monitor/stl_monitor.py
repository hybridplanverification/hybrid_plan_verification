'''
1. RTAMT- based STL monitoring framework
2. Input: 
     trace.csv
     formulas.txt
3. Output:
    robustness_table.csv
4. Online monitoring (reads one sample at a time)
5. Monitoring stops after Tmax is reached and the overall robustness has been finalized.

'''

import os
import csv
import time
import re
import math

import rtamt


class STLMonitor:

    def __init__(
        self,
        trace_file="stl_monitor/trace.csv",
        formula_file="stl_monitor/formulas.txt",
        output_file="stl_monitor/robustness_table.csv",
        poll_interval=0.01
    ):

        self.trace_file = trace_file
        self.formula_file = formula_file
        self.output_file = output_file
        self.poll_interval = poll_interval

        #--------------------------------formulas------------------------------------

        self.formulas = {}

        #--------------------------------online Stl monitor------------------------------------

        self.monitors = {}
        self.overall_monitor = None

        #--------------------------------previous and current states------------------------------------

        self.previous_state = None
        self.current_state = None

        #--------------------------------trace information------------------------------------

        self.columns = []
        self.header_read = False
        self.processed_rows = 0
        self.last_time = None

        #--------------------------------outputs------------------------------------

        self.output_initialized = False
        self.output_rows = []

        
        self.Tmax = 50.0

        self.final_overall = float("nan")

        
        
        self.overall_finalized = False
        self.running_robustness = {}

        self.load_formulas()

    # ---------------------------- load STL formulas ----------------------------

    def load_formulas(self):

        with open(
            self.formula_file,
            "r"
        ) as file:

            content = file.read()

        blocks = re.findall(
            r"(.*?)\s*:\s*\n(.*?)\nEND",
            content,
            re.DOTALL
        )

        self.formulas.clear()

        for name, formula in blocks:

            name = name.strip()
            formula = formula.strip()

            if name:
                self.formulas[name] = formula



    # ---------------------------- covert values into RTAMT specific numeric values ----------------------------

    def convert_value(self, value):

        if value is None:
            return 0.0

        if isinstance(value, bool):
            return float(int(value))

        if isinstance(value, (int, float)):

            if math.isnan(float(value)):
                return 0.0

            return float(value)

        value = str(value).strip()

        if value == "":
            return 0.0

        if value.lower() == "true":
            return 1.0

        if value.lower() == "false":
            return 0.0

        try:
            return float(value)

        except ValueError:
            return 0.0

    # ---------------------------- create rtamt monitor ----------------------------

    def create_online_monitor(
        self,
        formula,
        columns
    ):

        monitor = rtamt.StlDiscreteTimeSpecification()

        # ---------------------------- declare current state variables ----------------------------

        for column in columns:

            if column == "time":
                continue

            monitor.declare_var(
                column,
                "float"
            )

        # ---------------------------- declare previous state variables ----------------------------

        for column in columns:

            if column == "time":
                continue

            monitor.declare_var(
                "prev_" + column,
                "float"
            )

        # ---------------------------- set formula ----------------------------

        monitor.spec = formula

        # Parse formula.

        monitor.parse()

        # ---------------------------- convert future time operators ----------------------------

        monitor.pastify()

        return monitor

    # ---------------------------- create all monitors ----------------------------

    def create_monitors(self):

        print("\nCreating online RTAMT monitors...")

        self.monitors = {}

        for name, formula in self.formulas.items():

            print("  Creating:", name)

            monitor = self.create_online_monitor(
                formula,
                self.columns
            )

            self.monitors[name] = monitor


        self.running_robustness = {}

        for name, formula in self.formulas.items():
            operator = self.get_aggregation_operator(formula)
            self.running_robustness[name] = {
                "operator": operator,
                "value": None
            }

        # ---------------------------- create conjunction of all formulas ----------------------------

        if len(self.formulas) > 0:

            overall_formula = self.create_overall_formula()

            print("\nOverall formula:")
            print(overall_formula)

            self.overall_monitor = (
                self.create_online_monitor(
                    overall_formula,
                    self.columns
                )
            )

        print()

    # ---------------------------- determine aggregation operator ----------------------------

    def get_aggregation_operator(self, formula):
        
        formula = formula.strip()

        while formula.startswith("("):
            formula = formula[1:].lstrip()

        match = re.match(
            r"^(always|eventually|globally|G|F)\b",
            formula,
            re.IGNORECASE
        )

        if not match:
            return None

        operator = match.group(1).lower()

        if operator in ("always", "globally", "g"):
            return "min"

        return "max"

    # ---------------------------- update aggregate robustness ----------------------------

    def update_running_robustness(self, name, robustness):
        
        if math.isnan(robustness):
            return

        entry = self.running_robustness[name]
        operator = entry["operator"]
        previous = entry["value"]

        if previous is None:
            entry["value"] = robustness
        elif operator == "min":
            entry["value"] = min(previous, robustness)
        elif operator == "max":
            entry["value"] = max(previous, robustness)
        else:
            entry["value"] = robustness

    # ---------------------------- create overall conjunction ----------------------------

    def create_overall_formula(self):

        formulas = []

        for formula in self.formulas.values():

            formulas.append(
                "(" + formula + ")"
            )

        return "\nand\n".join(formulas)

    # ---------------------------- convert csv row into state ----------------------------

    def row_to_state(
        self,
        row
    ):

        state = {}

        for column in self.columns:

            if column not in row:
                continue

            if column == "time":

                state[column] = float(
                    row[column]
                )

            else:

                state[column] = (
                    self.convert_value(
                        row[column]
                    )
                )

        return state

    # ---------------------------- build monitor input ----------------------------

    def build_monitor_input(
        self,
        previous_state,
        current_state
    ):

        values = []

        # ----------------------------current values ----------------------------

        for column in self.columns:

            if column == "time":
                continue

            current_value = current_state.get(
                column,
                0.0
            )

            values.append(
                (
                    column,
                    self.convert_value(
                        current_value
                    )
                )
            )

        # ---------------------------- previous values ----------------------------

        for column in self.columns:

            if column == "time":
                continue

            previous_value = previous_state.get(
                column,
                current_state.get(
                    column,
                    0.0
                )
            )

            values.append(
                (
                    "prev_" + column,
                    self.convert_value(
                        previous_value
                    )
                )
            )

        return values

    # ---------------------------- extract robustness ----------------------------

    def extract_robustness(
        self,
        result
    ):

        if isinstance(
            result,
            (int, float)
        ):

            return float(result)

        if isinstance(
            result,
            (list, tuple)
        ):

            if len(result) == 0:
                return float("nan")

            if (
                len(result) == 2
                and isinstance(
                    result[1],
                    (int, float)
                )
            ):

                return float(
                    result[1]
                )

            for value in reversed(result):

                if isinstance(
                    value,
                    (int, float)
                ):

                    return float(value)

        return float("nan")

    # ---------------------------- initialize output ----------------------------

    def initialize_output(self):

        columns = ["time"]

        columns.extend(
            self.formulas.keys()
        )

        columns.append("overall")

        with open(
            self.output_file,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(columns)

        self.output_initialized = True

    # ---------------------------- write output row ----------------------------

    def write_output_row(
        self,
        timestamp,
        robustness_values,
        overall
    ):

        row = [timestamp]

        for name in self.formulas.keys():

            value = robustness_values.get(
                name,
                float("nan")
            )

            row.append(value)

        row.append(overall)

        with open(
            self.output_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(row)

    # ---------------------------- rewrite the output with final overall fromula----------------------------

    def rewrite_output_with_final_overall(self):

        if not self.output_rows:
            return

        if not self.overall_finalized:
            return

        # ---------------------------- change only overall and preseve the subformulas ----------------------------

        for row in self.output_rows:

            row[-1] = self.final_overall

        # Rewrite the complete CSV.

        with open(
            self.output_file,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            header = ["time"]

            header.extend(
                self.formulas.keys()
            )

            header.append("overall")

            writer.writerow(header)

            writer.writerows(
                self.output_rows
            )

    # ---------------------------- process new trace sample ----------------------------



    def process_sample(
        self,
        current_state
    ):

        if self.previous_state is None:

            previous_state = current_state.copy()

        else:

            previous_state = self.previous_state

        self.current_state = current_state.copy()

        timestamp = float(
            current_state["time"]
        )

        # ---------------------------- build current and previous signals ----------------------------

        monitor_input = self.build_monitor_input(
            previous_state,
            current_state
        )

        # ---------------------------- evaluate individual formulas ----------------------------

        robustness_values = {}

        for name, monitor in self.monitors.items():

            try:

                result = monitor.update(
                    timestamp,
                    monitor_input
                )

                robustness = self.extract_robustness(
                    result
                )

                robustness_values[name] = robustness

                # ---------------------------- determine aggregation operator ----------------------------

                formula = self.formulas[name].strip()

                match = re.match(
                    r"^\s*\(*\s*(always|eventually|globally|G|F)\b",
                    formula,
                    re.IGNORECASE
                )

                if match:

                    operator = match.group(1).lower()

                    if operator in (
                        "always",
                        "globally",
                        "g"
                    ):

                        aggregation = "min"

                    else:

                        aggregation = "max"

                else:

                    aggregation = "latest"

                # ---------------------------- initialize aggregation entry if necessary ----------------------------

                if (
                    name not in self.running_robustness
                    or self.running_robustness[name] is None
                    or not isinstance(
                        self.running_robustness[name],
                        dict
                    )
                ):

                    self.running_robustness[name] = {
                        "operator": aggregation,
                        "value": None
                    }

                entry = self.running_robustness[name]

                entry["operator"] = aggregation

                # ---------------------------- update aggregate ----------------------------

                if not math.isnan(robustness):

                    previous_value = entry["value"]

                    if previous_value is None:

                        entry["value"] = robustness

                    elif aggregation == "min":

                        entry["value"] = min(
                            previous_value,
                            robustness
                        )

                    elif aggregation == "max":

                        entry["value"] = max(
                            previous_value,
                            robustness
                        )

                    else:
                        entry["value"] = robustness

            except Exception as error:

                print(
                    "\nRTAMT error in formula "
                    + str(name)
                    + ":"
                )

                print(error)

                robustness_values[name] = float("nan")

        # ---------------------------- evaluate overall RTAMT formula ----------------------------

        overall = float("nan")

        if self.overall_monitor is not None:

            try:

                result = self.overall_monitor.update(
                    timestamp,
                    monitor_input
                )

                overall = self.extract_robustness(
                    result
                )

            except Exception as error:

                print(
                    "\nRTAMT error in overall formula:"
                )

                print(error)

        # ---------------------------- finalize after updating Tmax sample ----------------------------

        if (
            timestamp >= self.Tmax
            and not self.overall_finalized
        ):

            accumulated_values = [
                entry["value"]
                for entry in self.running_robustness.values()
                if (
                    isinstance(entry, dict)
                    and entry.get("value") is not None
                    and not math.isnan(entry["value"])
                )
            ]

            print(
                "\nAggregate robustness values of subformulas:"
            )

            for name, entry in self.running_robustness.items():

                if isinstance(entry, dict):

                    operator = entry.get(
                        "operator",
                        "latest"
                    )

                    value = entry.get(
                        "value"
                    )

                    print(
                        "  {} ({} aggregation) = {}".format(
                            name,
                            operator,
                            value
                        )
                    )

            if (
                accumulated_values
                and len(accumulated_values)
                == len(self.running_robustness)
            ):

                self.final_overall = min(
                    accumulated_values
                )

            else:

                self.final_overall = float("nan")

                print(
                    "\nWarning: Some subformula aggregates "
                    "are missing or invalid."
                )

            self.overall_finalized = True

            print(
                "\nOverall robustness = "
                "min(aggregate subformula values) = {}".format(
                    self.final_overall
                )
            )

            print(
                "\n--------------------------------------------------"
            )

            print(
                "FINAL OVERALL ROBUSTNESS"
            )

            print(
                "Interval: [0, {}]".format(
                    self.Tmax
                )
            )

            print(
                "Overall robustness = {}".format(
                    self.final_overall
                )
            )

            print(
                "------------------------------------------------------"
            )

        # ---------------------------- prepare output row ----------------------------

        row = [timestamp]

        for name in self.formulas.keys():

            value = robustness_values.get(
                name,
                float("nan")
            )

            row.append(value)

        if self.overall_finalized:

            row.append(
                self.final_overall
            )

        else:

            row.append(
                float("nan")
            )

        self.output_rows.append(row)

        # ---------------------------- update output CSV ----------------------------

        if self.overall_finalized:

            self.rewrite_output_with_final_overall()

        else:

            self.write_output_row(
                timestamp,
                robustness_values,
                float("nan")
            )

        # ---------------------------- store current state as previous state ----------------------------

        self.previous_state = current_state.copy()

        self.last_time = timestamp

    # ---------------------------- read trace header ----------------------------

    def read_header(
        self,
        file
    ):

        while True:

            position = file.tell()

            line = file.readline()

            if not line:

                time.sleep(
                    self.poll_interval
                )

                file.seek(position)

                continue

            line = line.strip()

            if line == "":
                continue

            reader = csv.reader(
                [line]
            )

            header = next(reader)

            self.columns = [
                column.strip()
                for column in header
            ]

            self.header_read = True

            print("\nTrace columns:")

            for column in self.columns:

                print(" ", column)

            return

    # ---------------------------- convert csv line into dictionary ----------------------------

    def parse_row(
        self,
        line
    ):

        reader = csv.reader(
            [line]
        )

        values = next(reader)

        if len(values) != len(self.columns):
            return None

        row = {}

        for index, column in enumerate(self.columns):

            row[column] = values[index].strip()

        return row

    # ---------------------------- online trace reader ----------------------------

    def monitor_trace(self):

        print(
            "\n-------------------------------------------------"
        )

        print("ONLINE STL MONITOR STARTED")

        print("Trace:", self.trace_file)

        print("Output:", self.output_file)

        print("Tmax:", self.Tmax)

        print(
            "--------------------------------------------------"
        )

        while not os.path.exists(
            self.trace_file
        ):

            print("Waiting for trace file...")

            time.sleep(
                self.poll_interval
            )

        with open(
            self.trace_file,
            "r"
        ) as file:

            self.read_header(file)

            self.create_monitors()

            self.initialize_output()

            while True:

                position = file.tell()

                line = file.readline()

                if not line:

                    file.seek(position)

                    time.sleep(
                        self.poll_interval
                    )

                    continue

                line = line.strip()

                if line == "":
                    continue

                row = self.parse_row(line)

                if row is None:

                    file.seek(position)

                    time.sleep(
                        self.poll_interval
                    )

                    continue

                # ---------------------------- convert row to state ----------------------------

                current_state = self.row_to_state(row)

                if "time" not in current_state:
                    continue

                # Process one sample.

                self.process_sample(current_state)
                
                self.processed_rows += 1

                # ---------------------------- stop after Tmax ----------------------------

                if (
                    current_state["time"] >= self.Tmax
                    and self.overall_finalized
                ):

                    print(
                        "\nTmax reached. Stopping online monitoring."
                    )

                    break                



            print("\nONLINE STL MONITORING FINISHED.")
            print("Processed samples:", self.processed_rows)

            if self.overall_finalized:

                print(
                    "Final overall robustness:",
                    self.final_overall
                )

            else:

                print(
                    "Warning: Tmax was reached, but the overall "
                    "robustness was not finalized."
                )

    # ---------------------------- run monitor ----------------------------

    def run(self):

        try:

            self.monitor_trace()

        except KeyboardInterrupt:

            print(
                "\n\nOnline STL monitoring stopped."
            )

        except Exception as error:

            print(
                "\n\nMonitor error:"
            )

            print(error)


# ---------------------------- standalone execution ----------------------------

if __name__ == "__main__":

    monitor = STLMonitor(
        trace_file="stl_monitor/trace.csv",
        formula_file="stl_monitor/formulas.txt",
        output_file="stl_monitor/robustness_table.csv"
    )

    monitor.run()
