
# -----------------------------------------------------------------------------
# File: projectroom3.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
import time as t
import sqlite3
from .utils import chooseNextRoom

def enterProjectRoom3(state, saveName, time_played, startTime):
    # --- Check if the player has the key to enter ---
    if not state["visited"]["projectroom3"]:
        if "project key" not in state["inventory"]:
            print("\n🚪 The door to Project Room 3 is locked.")
            print("You jiggle the handle. It's no use.")
            print("🔐 You need a key. Perhaps it's hidden elsewhere in the school?")
            return "corridor"
        else:
            print("\n🗝️ You insert the brass key into the lock and turn it with a satisfying click.")
            print("The door creaks open to reveal a bright and lively workspace.")

    # --- Room entry description ---
    print("\n🏗️ You enter Project Room 3.")
    print("Several tables are pushed together, covered in papers, laptops, and half-eaten snacks.")
    print("A group of students is finishing a project while chatting and laughing.")

    # --- Command handlers ---

    def handle_look():
        """Describe the room and give clues."""
        print("\nYou scan the room.")
        print("The walls are covered in sticky notes, whiteboards are full of pseudocode and diagrams.")
        if not state["visited"]["projectroom3"]:
            print("Near the snack table, one student holds up a fruit and says:")
            print("'You know what they say... which fruit keeps the doctor away?'")
            print("Another grins and says, 'Classic. We always bring them during hackathons.'")
            print("Seems like a riddle. Maybe it's part of the challenge?")
        else:
            print("The students have left. Only empty wrappers and a few notebooks remain.")
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """List available commands."""
        print("\nAvailable commands:")
        print("- look around         : Examine the room for clues.")
        if not state["visited"]["projectroom3"]:
            print("- answer <fruit>      : Solve the riddle about the fruit.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")
        print("- pause                : Pause the game.")

    def handle_go(destination):
        """Handle movement out of the room."""
        if destination in ["corridor", "back"]:
            print("You step away from the lively room and return to the corridor.")
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer):
        """Handle the fruit riddle."""
        if state["visited"]["projectroom3"]:
            print("✅ You've already completed this room.")
            return None
        normalized = answer.strip().lower()
        if normalized in ["apple", "an apple", "apples"]:
            print("✅ Correct! One of the students claps. 'Of course. Apples every time.'")
            state["visited"]["projectroom3"] = True
            state["previous_room"] = "projectroom3"
            print("\n🎉 CONGRATULATIONS!")
            print("You've explored all the essential rooms of the school.")
            print("Your adventure through logic, memory, and mystery ends here.")
            print("\n🏆 You completed the game! 🏆")

            handle_pause()

    def handle_pause():
        # state: the dictionary storing current room, previous room, inventory, and visited rooms
        #saveName: the name of the save file (or "no save" if it's a new game)
        #time_played: total time played in previous sessions (in seconds)
        conn = sqlite3.connect("NewSave.db")
        cur = conn.cursor()
        elapsed_time = (t.time() - startTime) + time_played

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



    # --- Main command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            guess = command[7:].strip()
            result = handle_answer(guess)
            if result:
                return result

        elif command == "pause":
            handle_pause()
            sys.exit()

        elif command == "quit":
            print("👋 You close your notebook and leave the project behind. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
