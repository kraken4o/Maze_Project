# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
import time as t
import sqlite3
from .utils import chooseNextRoom

def enterStudyLandscape(state, saveName, time_played, startTime):
    state["visited"]["studylandscape"] = True
    print("\n🛋️ You step into the study landscape.")
    print("Soft chairs and tables to work and chat with fellow students and a quiet hum of a coffee machine.")
    print("It feels like a place to work but also to pause and catch your breath.")

    # --- Command handlers ---

    def handle_look():
        """Describe the lobby and show exits."""
        print("\nYou take a slow look around.")
        print("There are a few posters on the wall about upcoming student events.")
        print("A group of students is sitting in the corner gazing at a laptop")
        print("- Possible exit: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """Show help message with available commands."""
        print("\nAvailable commands:")
        print("- look around         : See what’s in the lobby.")
        print("- go corridor / back  : Return to the main corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print("- pause                : Pause the game.")

    def handle_go(destination):
        """Handle movement to another room."""
        if destination in ["corridor", "back"]:
            print("You leave the study landscape and head back into the corridor.")
            state["previous_room"] = "studylandscape"
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

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

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "quit":
            print("👋 You sit back in the softest chair, close your eyes, and exit the adventure. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
