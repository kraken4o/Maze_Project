# -----------------------------------------------------------------------------
# File: classroom2015.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
import sqlite3
import sys
import time as t
from math import ceil

from .utils import chooseNextRoom

def enterClassroom2015(state, saveName,time_played,startTime):
    print("\n🏫 You step into Classroom 2.015.")
    print("The classroom is filled with students. A teacher turns toward you, visibly annoyed.")
    print("The door creaks shut behind you. Everyone is looking at you; it's completely silent.")

    # --- Helperfuncties voor commandoverwerking ---

    def handle_look():
        print("\nYou take a careful look around the room.")
        print("At the front is a whiteboard completely filled with formulas.")
        print("Desks with students are arranged in neat rows, though one chair is oddly turned toward the window.")
        print("On the teacher's desk, a calculator is lying in a strange position on the table.")
        if not state["visited"]["classroom2015"]:
            print("The teacher says, you are late! And he asks you a question:")
            print("\"What is 7 * 6?\"")
        else:
            print("The teacher sighs: You again? You already solved the challenge.")
            if "storage_key" not in state["inventory"]:
                print("On the desk, beneath the calculator, something metallic glints. It looks like a small storage key.")
            else:
                print("The desk is empty. You've already taken the storage key.")
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its contents.")
        if not state["visited"]["classroom2015"]:
            print("- answer <number>     : Attempt to solve the math question.")
        if state["visited"]["classroom2015"] and "storage_key" not in state["inventory"]:
            print("- take storage_key            : Pick up the storage key once it's revealed.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- status              : Show game status.")
        print("- pause               : Pause the game.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "storage_key":
            if not state["visited"]["classroom2015"]:
                print("❌ There's no key visible yet. Maybe solving the puzzle will reveal more.")
            elif "storage_key" in state["inventory"]:
                print("You already have the storage key in your backpack.")
            else:
                print("🔑 You lift the calculator from te desk and find a small storage key underneath.")
                print("You take it and tuck it safely into your backpack.")
                state["inventory"].append("storage_key")
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
        elif answer == "42":
            print("✅ Correct! The teacher invites you to the desk.")
            state["visited"]["classroom2015"] = True
            print("Suddenly you see something on the desk.")
        else:
            print("❌ Incorrect. The teacher opens the door of the classroom.")
            print("You are gently guided back into the corridor.")
            return "corridor"

    def handle_status():
        count = 0  # Initialize inside the function
        for room, visited in state["visited"].items():
            if visited:
                count += 1
        perc = (count / len(state['visited'])) * 100
        print("Save name: ",saveName)
        print("Time played: ",time_played)
        print(f"{ceil(perc)}% of rooms visited")

    def handle_pause(state, saveName, time_played, startTime):

        elapsed_time = (t.time() - startTime) + time_played
        flag = True
        conn = sqlite3.connect("NewSave.db")
        cur = conn.cursor()
        # collect relavant IDs of the rooms in the current game file being played
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
                "UPDATE Saves SET currentId = ?, previousId = ?, time = ? WHERE saveId = ?",
                (currentId, previousId, float(elapsed_time), saveId)
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
                "INSERT INTO Saves (saveName, currentId, previousId, time) VALUES (?, ?, ?, ?)",
                (saveName, currentId, previousId, float(elapsed_time))
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

    # --- Commandoloop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command=="status":
            handle_status()

        elif command=="pause":
            handle_pause(state,saveName,time_played,startTime)

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
