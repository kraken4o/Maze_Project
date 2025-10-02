# -----------------------------------------------------------------------------
# File: equinoxroom.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2025
# -----------------------------------------------------------------------------
import sqlite3
import sys
from .utils import chooseNextRoom

def enterEquinoxroom(state, saveName, time, startTime):
    if not state["visited"]["equinoxroom"]:
        if "equinox key" not in state["inventory"]:
            print("\n🚪 A man with black robe stands in front of the door")
            print("'You are not allowed to enter'")
            print("🔐 You need a key. But where could it be?")
            return "corridor"
        else:
            print("🗝️ You insert and turn the equinox key and you hear gears moving")
            print("The heavy door opens and bright light flashes you")

    if not state["visited"]["equinoxroom"]:
        print("Welcome in Equinox room")
    else:
        print("It's you again")

    # --- Helperfuncties voor commandoverwerking ---

    def handle_look():
        print("\nYou take a careful look around the room.")
        print("Inside are 5 people wearing special Equinox t-shirts")
        print("You see a foosball and a vending machine- this room is exciting")
        print("The walls are covered in posters")
        if not state["visited"]["equinoxroom"]:
            #first visit, puzzle not solved
            print("The door shuts down and you see a big boy blocking the door")
            print("'You have to feed me the right 3 snacks and I'll let you leave!'")
            print("Panicked you go straight the vending machine")
            print("You see 5 items in the machine - cola, chips, stroopwafel, beer, kitkat")
        else:
            #already visited, puzzle solved
            print("'Welcome back! Relax and take your time!'")
            #key is not taken
            if "project key" not in state["inventory"]:
                print("You forgot to take your project key and it's awaiting you on top of the foosball")
            else:
                #key is taken
                print("You took the project key last time")
        if state["solved_vending"]:
            #exit is possible after solving puzzle
            print("- Possible exits: corridor")
        else:
            print("- Possible exits: currently blocked")
        print("- Your current inventory:", state["inventory"])

    # --- basic states ---

    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its contents.")
        if not state["visited"]["equinoxroom"]:
            #input 3 strings separated by space
            print("- answer <3 items>     : You have to give the correct 3 items separated by comma.")
        if state["visited"]["equinoxroom"] and "project key" not in state["inventory"]:
            print("- take project key            : Pick up the project key once it's revealed.")
        if not state["visited"]["equinoxroom"]:
            print("- go command is currently disabled due to uncompleted puzzle")
        else:
            print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- pause               : Pause the game.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "project key":
            #first visit, not solved puzzle, no key
            if not state["visited"]["equinoxroom"]:
                print("Maybe the key is in the big boy?")
            #check for key
            elif "project key" in state["inventory"]:
                print("You already have the project key in your backpack.")
            else:
                #get key after completing puzzle
                print("🔑 You take the project key from the big boy")
                print("You take it and tuck it safely into your backpack.")
                state["inventory"].append("project key")
        else:
            #any item that is not the key
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["corridor", "back"]:
            #can't go back if puzzle is not solved
            if not state.get("solved_vending",False):
                print("You can't go because the big boy is blocking the door")
            else:
                #puzzle solved, can leave
                print("🚪 You open the door and step back into the corridor.")
                return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")

    def handle_pause(state, saveName, time, startTime):

        flag = True
        conn = sqlite3.connect("GameSave.db")
        cursor = conn.cursor()
        if saveName == "test":
            userName = input("enter name of save file: ")
            while flag:
                cursor.execute("""SELECT saveName FROM saves WHERE saveName = ?""", (userName,))
                saveList = cursor.fetchall()
                if saveList:
                    userName = input("save file already exists enter name of save file: ")
                else:
                    cursor.execute("""INSERT INTO Saves (saveName, state) VALUES (?, ?)""", (userName, str(state)))
                    conn.commit()
                    sys.exit()
        else:
            cursor.execute("""UPDATE Saves SET state = ? WHERE saveName = ?""", (str(state), saveName))
            conn.commit()
            sys.exit()


    # --- Extra state for the vending machine puzzle ---

    #initialize puzzle state
    if "chosen_items" not in state:
        state["chosen_items"] = []
    if "solved_vending" not in state:
        state["solved_vending"] = False

    correct_items = {"chips", "beer", "stroopwafel"}

    #handles puzzles and requires exactly 3 items
    def handle_answer(answer):
        if state["visited"]["equinoxroom"]:
            print("You already fed big boy")
        else:
            items = [item.strip() for item in answer.split(",")]

            if len(items) != 3:
                print("❌ You must choose exactly 3 items using comas")
                return
            #turn the list into set(no duplicates)
            state["chosen_items"] = set(items)
            #makes intersection, checks how much of the items match and turns that to int
            correct_count = len(state["chosen_items"] & correct_items)

            # if 3 out of 3 items are correct- puzzle solved
            if correct_count == 3:
                print("🎉 The big boy shouts: 'Finally, you picked the right snacks and passed the test!'")
                print("Officially you are the new member of Equinox")
                print("This grants you access to the special project key")
                state["visited"]["equinoxroom"] = True
                state["solved_vending"] = True
            #some of the items are not correct
            else:
                print(f"🤨 The big boy shakes his head: 'Hmm… {correct_count} of those are right.'")
                print("Try again!")

    # --- Commandoloop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command=="pause":
            handle_pause(state,saveName,time,startTime)

        elif command.startswith("take "):
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            answer = command[7:].strip()
            result = handle_answer(answer)
            if result:
                return result

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")