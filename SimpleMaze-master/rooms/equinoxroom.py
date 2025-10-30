# -----------------------------------------------------------------------------
# File: equinoxroom.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2025
# -----------------------------------------------------------------------------

import sqlite3
import sys
import time as t
from math import ceil
from .utils import chooseNextRoom

def enterEquinoxroom(state, saveName, time_played, startTime):
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

    # --- basic states---

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
        print("- status              : Show game status.")
        print("- pause               : Pause the game.")
        print("- scoreboard          : Show top 5 scores.")
        print("- quit                : Quit the game entirely.")
        print(f"- current inventory  : {state['inventory']}")


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

    def handle_status():
        elapsed_time = (t.time() - startTime) + time_played
        completed = 0
        totalgame = 0
        for i in state["visited"]:
            totalgame += 1
            if state["visited"][i]:
                completed += 1
        percentplayed = completed / totalgame * 100
        print(saveName, ":")
        print(f"you have completed {percentplayed:.1f}% of the game")
        print("time played:", elapsed_time)
        return percentplayed, elapsed_time

    def handle_scoreboard():

        conn = sqlite3.connect("GameSave.db")
        cur = conn.cursor()

        cur.execute("SELECT saveName, time, completion FROM saves")
        completionList = cur.fetchall()

        sorted_records = sorted(completionList, key=lambda x: (-x[2], x[1]))

        # Get top n records
        top_scores = sorted_records[:5]

        # Print results
        print("Top Scores:")
        for name, time, percent in top_scores:
            print(f"Name: {name}, Time: {time}, Percent: {percent}%")

    def handle_pause():

        # --- Calculate how long the player has been playing for ---
        # Combine saved play time with current session duration
        percentComplete, elapsed_time = handle_status()

        conn = sqlite3.connect("GameSave.db")
        cur = conn.cursor()

        # collect relevant IDs of the rooms in the current game file being played
        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["current_room"],))
        currentId = cur.fetchone()[0]

        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["previous_room"],))
        previousId = cur.fetchone()[0]

        cur.execute("""SELECT saveId FROM Saves WHERE saveName = ?""", (saveName,))
        saveId = cur.fetchone()

        if saveId:
            saveId = saveId[0]

            #  if there is already a saveID that has the current save name it updates the rooms and time played
            cur.execute(
                "UPDATE Saves SET currentId = ?, previousId = ?, time = ?, completion = ? WHERE saveId = ?",
                (currentId, previousId, float(elapsed_time), float(percentComplete), saveId)
            )

            # deletes all room states for a save id and iterates through the state of each room and adds it back in
            cur.execute("DELETE FROM SaveRoomState WHERE saveId = ?", (saveId,))
            for room_name, visited in state.get("visited", {}).items():
                cur.execute("SELECT roomId FROM Rooms WHERE roomName = ?", (room_name,))
                r = cur.fetchone()
                if r:
                    cur.execute(
                        "INSERT INTO SaveRoomState (saveId, roomId, visited) VALUES (?, ?, ?)",
                        (saveId, r[0], 1 if visited else 0)
                    )

            # deletes all items from inventory for a save id and iterates through the current files inventory and adds it back in
            cur.execute("DELETE FROM SaveInventory WHERE saveId = ?", (saveId,))
            for item_name in state.get("inventory", []):
                cur.execute("SELECT itemId FROM Items WHERE itemName = ?", (item_name,))
                i = cur.fetchone()
                if i:
                    cur.execute(
                        "INSERT INTO SaveInventory (saveId, itemId) VALUES (?, ?)",
                        (saveId, i[0])
                    )
        else:
            # If it doesn't exist, create a new one with that name
            cur.execute(
                "INSERT INTO Saves (saveName, currentId, previousId, time, completion) VALUES (?, ?, ?, ?, ?)",
                (saveName, currentId, previousId, float(elapsed_time), float(percentComplete))
            )
            save_id = cur.lastrowid

            # --- Update SaveRoomState table to reflect visited rooms ---
            for room_name, visited in state.get("visited", {}).items():
                cur.execute("SELECT roomId FROM Rooms WHERE roomName = ?", (room_name,))
                r = cur.fetchone()
                if r:
                    cur.execute(
                        "INSERT INTO SaveRoomState (saveId, roomId, visited) VALUES (?, ?, ?)",
                        (save_id, r[0], 1 if visited else 0)
                    )

            # --- Update SaveInventory table with player's items ---
            for item_name in state.get("inventory", []):
                cur.execute("SELECT itemId FROM Items WHERE itemName = ?", (item_name,))
                i = cur.fetchone()
                if i:
                    cur.execute(
                        "INSERT INTO SaveInventory (saveId, itemId) VALUES (?, ?)",
                        (save_id, i[0])
                    )

        # --- Commit changes to the database ---
        conn.commit()
        print(f"💾 Save '{saveName}' updated successfully!")
        print(f"Total playtime: {elapsed_time:.2f} seconds.")
        conn.close()
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

            # if 3 out of 3 items are correct puzzle solved
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
            handle_pause()

        elif command=="status":
            handle_status()

        elif command=="scoreboard":
            handle_scoreboard()

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
            handle_answer(answer)
            if result:
                return result

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")