# -----------------------------------------------------------------------------
# File: classroom2015.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2025
# -----------------------------------------------------------------------------

import sys
import time as t
import sqlite3
from .utils import chooseNextRoom


def enterTeacherroom(state, saveName, time_played, startTime):
    if "teacherroom" not in state["visited"]:
        state["visited"]["teacherroom"] = False

    if "teacher_key" not in state["inventory"]:
        print("\n🚪 The door to Project Room 3 is locked.")
        print("You jiggle the handle. It's no use.")
        print("🔐 You need a key. Perhaps it's hidden elsewhere in the school?")
        return "corridor"
    else:
        print("\n🗝️ You insert the teacher key into the lock and turn it with a satisfying click.")
        print("The door creaks open to reveal a bright and lively workspace.")

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
        else:
            print("The teacher sighs: You again? You already solved the challenge.")
            if "class key" not in state["inventory"]:
                print(
                    "On the desk, beneath the calculator, something metallic glints. It looks like a small class key.")
            else:
                print("The desk is empty. You've already taken the class key.")
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its contents.")
        if not state["visited"]["teacherroom"]:
            print("- answer <number>     : Attempt to solve the math question.")
        if state["visited"]["teacherroom"] and "class key" not in state["inventory"]:
            print("- take class key            : Pick up the class key once it's revealed.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "class key":
            if not state["visited"]["teacherroom"]:
                print("❌ There's no key visible yet. Maybe solving another puzzle will reveal more.")
            elif "class key" in state["inventory"]:
                print("You already have the storage key in your backpack.")
            else:
                print("🔑 You lift the calculator from the desk and find a class key underneath.")
                print("You take it and tuck it safely into your backpack.")
                state["inventory"].append("class key")
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
        if state["visited"]["teacherroom"]:
            print("✅ You've already solved this challenge.")
        elif answer == "20":
            print("✅ Correct! You can now go to the next room.")
            state["visited"]["teacherroom"] = True
        else:
            print("Incorrect")
            return "corridor"

    def handle_pause(state, saveName, time_played, startTime):

        elapsed_time = (t.time() - startTime) + time_played
        flag = True
        conn = sqlite3.connect("GameSave.db")
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

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
