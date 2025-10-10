
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

            conn = sqlite3.connect("GameSave.db")
            cursor = conn.cursor()
            elapsed_time = (t.time() - startTime) + time_played
            if saveName == "no save":
                # Ask player for a new save file name
                userName = input("enter name of save file: ")
                while True:
                    # Check if the save file already exists
                    cursor.execute("""SELECT saveName FROM saves WHERE saveName = ?""", (userName,))
                    saveList = cursor.fetchall()
                    if saveList:
                        userName = input("save file already exists enter name of save file: ")
                    else:
                        cursor.execute("""INSERT INTO saves (saveName, state, saveTime) VALUES (?, ?, ?)""",
                                       (userName, str(state), elapsed_time))
                        conn.commit()
                        print(f"Total playtime: {elapsed_time:.2f} seconds.")
                        sys.exit()
            else:
                cursor.execute("""UPDATE Saves SET state = ?, saveTime = ? WHERE saveName = ?""",
                               (str(state), elapsed_time, saveName))
                conn.commit()
                print(f"Total playtime: {elapsed_time:.2f} seconds.")
                sys.exit()
        else:
            print("❌ The student shrugs. 'Nope, that one's not it. Think classic.'")
            print("You decide to step out and think it over.")
            return "corridor"

    def handle_pause(state, saveName, time_played, startTime):
    # state: the dictionary storing current room, previous room, inventory, and visited rooms
    #saveName: the name of the save file (or "no save" if it's a new game)
    #time_played: total time played in previous sessions (in seconds)
        flag = True
        conn = sqlite3.connect("GameSave.db")
        cursor = conn.cursor()

        #elapsed time is the total time accross all sessions
        elapsed_time = (t.time() - startTime) + time_played
        #t.time() here is the seconds since the epoch(Jan 1, 1970) when you hit pause
        #Starttime is in the main function and is also the seconds since the epoch but was taken earlier, when you enter your file to run the game.
        #time played adds the previous to the current seconds played ofn the same file
        if saveName == "no save":
            # Ask player for a new save file name
            userName = input("enter name of save file: ")
            while flag:
                # Check if the save file already exists
                cursor.execute("""SELECT saveName FROM saves WHERE saveName = ?""", (userName,))
                saveList = cursor.fetchall()
                if saveList:
                    userName = input("save file already exists enter name of save file: ")
                else:
                    cursor.execute("""INSERT INTO saves (saveName, state, saveTime) VALUES (?, ?, ?)""", (userName, str(state), elapsed_time))
                    #new file adds states and elapsedtime
                    conn.commit()
                    print(f"💾 Game saved successfully! Total playtime: {elapsed_time:.2f} seconds.")
                    sys.exit()
        else:
            #updated the old databsee file with new state and elapsed time
            cursor.execute("""UPDATE Saves SET state = ?, saveTime = ? WHERE saveName = ?""", (str(state), elapsed_time, saveName))
            conn.commit()
            print(f"💾 Game updated successfully! Total playtime: {elapsed_time:.2f} seconds.")
            sys.exit()


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
            handle_pause(state, saveName, time_played, startTime)

        elif command == "quit":
            print("👋 You close your notebook and leave the project behind. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
