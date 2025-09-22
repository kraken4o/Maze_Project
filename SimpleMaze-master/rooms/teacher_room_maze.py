# -----------------------------------------------------------------------------
# File: classroom2015.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2025
# -----------------------------------------------------------------------------

import sys
from .utils import chooseNextRoom

def enterteacher_room_maze(state):
    print("\n🏫 You step into Teacher Room")
    print("The room is empty with only clues in different places")

    # --- Helperfuncties voor commandoverwerking ---

    def handle_look():
        print("\nYou take a careful look around the room.")
        print("Around the room are different clues for how to get out")
        print("On the teacher's desk, a calculator is lying in a strange position on the table.")
        if not state["visited"]["teacherroom"]:
            print("You find a note with a clue:")
            print("you need to solve a question to get the clue")
            print("\"What is 5 * 4?\"")


    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its contents.")
        if not state["visited"]["teacherroom"]:
            print("- answer <number>     : Attempt to solve the math question.")
        if state["visited"]["teacherroom"] and "key" not in state["inventory"]:
            print("- take key            : Pick up the key once it's revealed.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "key":
            if not state["visited"]["teacherroom"]:
                print("❌ There's no key visible yet. Maybe solving another puzzle will reveal more.")

                print("🔑 You lift the calculator from the desk and find a small brass key underneath.")
                print("You take it and tuck it safely into your backpack.")
                state["inventory"].append("key")
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["corridor", "back"]:
            print("🚪 You open the door and step back into the corridor.")
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer):
        if state["visited"]["classroom2015"]:
            print("✅ You've already solved this challenge.")
        elif answer == "20":
            print("✅ Correct! You can now go to the next room.")
            state["visited"]["teacherroom"] = True

