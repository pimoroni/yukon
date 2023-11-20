import os
from collections import namedtuple

"""
GCodeParser is a class for processing G-Code files into movement
and pen height commands for use with a CNC plotter.

Only a subset of G-Code commands are supported:
- G0/G1 - Linear Move
- G90 - Absolute Positioning
- G91 - Relative Positioning
- M3 - Spindle CW / Laser On (used to lower the pen to the page)
- M4 - Spindle CCW / Laser On (used to raise the pen just above the page)
- M5 - Spindle / Laser Off (used to raise the pen to its home position)
"""

Rect = namedtuple("Rect", ("x", "y", "width", "height"))


class GCodeParser:
    ABSOLUTE_POSITIONING = 0
    RELATIVE_POSITIONING = 1

    def __init__(self, absolute_callback=None, relative_callback=None, lower_pen_callback=None, lift_pen_callback=None, raise_pen_callback=None, root="/"):
        self.__positioning_mode = GCodeParser.ABSOLUTE_POSITIONING
        self.__gcode = []
        self.__rect = None
        self.__origin_x = 0
        self.__origin_y = 0
        self.__normaliser = 1

        # Set the directory to search for files in
        self.set_root(root)

        self.__movement_index = -1

        self.__absolute_callback = absolute_callback
        self.__relative_callback = relative_callback
        self.__lower_pen_callback = lower_pen_callback
        self.__lift_pen_callback = lift_pen_callback
        self.__raise_pen_callback = raise_pen_callback

    def set_root(self, root):
        self.__root = root.rstrip("/") + "/"

    def load_file(self, gcode_file):
        if os.listdir(self.__root).count(gcode_file) == 0:
            raise ValueError(f"'{gcode_file}' not found")

        # Open the GCode file for reading
        with open(gcode_file, 'r') as file:
            for line in file:
                self.__gcode.append(line)

        self.__rect = GCodeParser.__calculate_rect(self.__gcode)

    def is_parsing(self):
        return self.__movement_index >= 0

    def start_parsing(self, origin_x, origin_y, size):
        if not self.is_parsing():
            self.__movement_index = 0

        self.__origin_x = origin_x
        self.__origin_y = origin_y

        self.__normaliser = size / max(self.__rect.width, self.__rect.height)

    def parse_next(self):
        if not self.is_parsing():
            raise RuntimeError("Cannot process gcode commands until plotting has been started")

        if self.__movement_index >= len(self.__gcode):
            self.__movement_index = -1
            return False

        gcode_line = self.__gcode[self.__movement_index]
        command_parts = gcode_line.split()      # Split the G-code command into its components
        command_letter = command_parts[0]       # Extract the command letter

        # Extract numeric parameters from the command
        parameters = {}
        for part in command_parts[1:]:
            code = part[0]
            value = float(part[1:])
            parameters[code] = value

        # Process positioning mode commands
        if command_letter == "G90":
            self.__positioning_mode = GCodeParser.ABSOLUTE_POSITIONING
            print("Switching to Absolute Positioning")
        elif command_letter == "G91":
            self.__positioning_mode = GCodeParser.RELATIVE_POSITIONING
            print("Switching to Relative Positioning")

        # Process linear move commands
        elif command_letter == "G0" or command_letter == "G00" or \
                command_letter == "G1" or command_letter == "G01":

            # Extract the coordinates from the command
            x = parameters.get('X', None)
            y = parameters.get('Y', None)

            if self.__positioning_mode == GCodeParser.ABSOLUTE_POSITIONING:
                next_x = ((x - self.__rect.x) * self.__normaliser) + self.__origin_x
                next_y = ((y - self.__rect.y) * self.__normaliser) + self.__origin_y

                if self.__absolute_callback is not None:
                    self.__absolute_callback(next_x, next_y)
            else:
                next_dx = x * self.__normaliser
                next_dy = y * self.__normaliser

                if self.__relative_callback is not None:
                    self.__relative_callback(next_dx, next_dy)

        # Process Spindle / Laser CW
        elif command_letter == 'M03':
            if self.__lower_pen_callback is not None:
                self.__lower_pen_callback()

        # Process Spindle / Laser CCW
        elif command_letter == 'M04':
            if self.__lift_pen_callback is not None:
                self.__lift_pen_callback()

        # Process Spindle Off
        elif command_letter == 'M05':
            if self.__raise_pen_callback is not None:
                self.__raise_pen_callback()

        # Add more conditions for other G-code commands as needed
        else:
            print(f"Unsupported G-code command: {command_letter}")

        self.__movement_index += 1
        return True

    def __calculate_rect(gcode):
        current_x = 0
        current_y = 0
        max_x = float('-inf')
        min_x = float('inf')
        max_y = float('-inf')
        min_y = float('inf')
        positioning_mode = GCodeParser.ABSOLUTE_POSITIONING

        if len(gcode) <= 0:
            raise RuntimeError("Cannot calculate the rectangle of an empty gcode file")

        for index in range(len(gcode)):
            command_parts = gcode[index].split()    # Split the G-code command into its components
            command_letter = command_parts[0]       # Extract the command letter

            # Extract numeric parameters from the command
            parameters = {}
            for part in command_parts[1:]:
                code = part[0]
                value = float(part[1:])
                parameters[code] = value

            # Process positioning mode commands
            if command_letter == "G90":
                positioning_mode = GCodeParser.ABSOLUTE_POSITIONING
            elif command_letter == "G91":
                positioning_mode = GCodeParser.RELATIVE_POSITIONING

            # Process movement commands
            elif command_letter == "G0" or command_letter == "G00" or \
                    command_letter == "G1" or command_letter == "G01":

                # Extract the coordinates from the command
                x = parameters.get('X', None)
                y = parameters.get('Y', None)

                # Update the current position with the coordinates, depending on the mode
                if positioning_mode == GCodeParser.ABSOLUTE_POSITIONING:
                    current_x = x
                    current_y = y
                else:
                    current_x += x
                    current_y += y

                max_x = max(current_x, max_x)
                min_x = min(current_x, min_x)
                max_y = max(current_y, max_y)
                min_y = min(current_y, min_y)

        width = max_x - min_x
        height = max_y - min_y
        return Rect(min_x, min_y, width, height)
