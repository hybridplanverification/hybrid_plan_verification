'''
ENHSP plan parser:
ENHSP plans in the form of: 
	0: -----waiting---- [10.0]
	10.0: (decelerate)
	10.0: -----waiting---- [12.0]
	12.0: (accelerate)
	12.0: -----waiting---- [14.0]
	14.0: (stop)
Retuens the list of events in chronological order

'''

import re
from dataclasses import dataclass
from typing import List, Union


#----------------------------Plan Event class-------------------------

#wait event for continuous process
@dataclass
class WaitEvent:
    start: float
    end: float

    @property
    def duration(self):
        return self.end - self.start


#action event for actions
@dataclass
class ActionEvent:
    time: float
    name: str
    parameters: List[str]


PlanEvent = Union[WaitEvent, ActionEvent]


#----------------------------ENHSP plan parser-------------------------
class ENHSPPlanParser:

    WAIT_PATTERN = re.compile(
        r'^\s*([\d\.]+)\s*:\s*-+waiting-+\s*\[([\d\.]+)\]\s*$',
        re.IGNORECASE
    )

    ACTION_PATTERN = re.compile(
        r'^\s*([\d\.]+)\s*:\s*\((.*?)\)\s*$'
    )

    def __init__(self, filename):

        self.filename = filename
        self.events: List[PlanEvent] = []

    #----------------------------parse the comlete plan-------------------------

    def parse(self):

        self.events.clear()

        with open(self.filename, "r") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith(";"):
                    continue

                if "waiting" in line.lower():

                    self.events.append(
                        self._parse_wait(line)
                    )

                elif "(" in line:

                    self.events.append(
                        self._parse_action(line)
                    )

        return self.events

    #----------------------------parse waiting interval-------------------------

    def _parse_wait(self, line):

        match = self.WAIT_PATTERN.match(line)

        if match is None:

            raise ValueError(
                f"Invalid waiting line:\n{line}"
            )

        return WaitEvent(
            start=float(match.group(1)),
            end=float(match.group(2))
        )

    #----------------------------parse action-------------------------

    def _parse_action(self, line):

        match = self.ACTION_PATTERN.match(line)

        if match is None:

            raise ValueError(
                f"Invalid action line:\n{line}"
            )

        time = float(match.group(1))

        tokens = match.group(2).strip().split()

        return ActionEvent(
            time=time,
            name=tokens[0].lower(),
            parameters=tokens[1:]
        )

    #----------------------------print events-------------------------

    def print_events(self):

        print("\n---------- Parsed Plan ----------\n")

        for event in self.events:

            if isinstance(event, WaitEvent):

                print(
                    f"WAIT   : "
                    f"{event.start:.3f} -> {event.end:.3f} "
                    f"(duration={event.duration:.3f})"
                )

            else:

                if event.parameters:

                    params = " ".join(event.parameters)

                    print(
                        f"ACTION : "
                        f"{event.time:.3f} "
                        f"{event.name} {params}"
                    )

                else:

                    print(
                        f"ACTION : "
                        f"{event.time:.3f} "
                        f"{event.name}"
                    )

        print("\n----------------------------------------\n")
