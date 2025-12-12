import os
import time
import schedule
from dotenv import load_dotenv
from mojang import API
# Import everything from definitions.py (ensure it's in the same directory)
from definitions import (
    get_player_infos,
    print_player_info,
    create_ref_data,
    export_ref_data_txt,
    create_comp_data,
    export_comp_data_txt,
    run_automation_cycle
)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("HYPIXEL_API_KEY")
BAZAAR_API_URL = "https://api.hypixel.net/v2/skyblock/bazaar"

def get_uuid(username: str) -> str:
    """Wrapper to get UUID using mojang API."""
    try:
        mojang_api = API()
        return mojang_api.get_uuid(username)
    except Exception as e:
        print(f"Error fetching UUID: {e}")
        return None

def main():
    if not API_KEY:
        print("CRITICAL WARNING: HYPIXEL_API_KEY not found in .env file.")
        print("Please create a .env file based on .env.example and add your API Key.")
        # We can continue for features that don't strictly need it if any, but most do.
    
    # Schedule the automation
    # Note: 'days_running' logic needs state management if we want it perfect, 
    # but for now using a simple global or passing 0 is fine as per original logic.
    days_running = 0 
    schedule.every(1).hours.do(run_automation_cycle, api_url=BAZAAR_API_URL, days_running=days_running)

    print("=== Hypixel Skyblock Tool ===")
    
    while True:
        mode = input(
            "\nSelect Mode:\n"
            "[I] Inspect Player Stats\n"
            "[R] Update Reference Prices\n"
            "[C] Update Comparison Prices\n"
            "[A] Automatic Mode\n"
            "[Q] Quit\n"
            "> "
        ).upper()

        if mode == "I":
            if not API_KEY:
                print("API Key required for this feature.")
                continue
                
            username = input("Username: ")
            uuid = get_uuid(username)
            if uuid:
                infos = get_player_infos(API_KEY, uuid)
                print_player_info(infos)
            else:
                print("Player not found.")

        elif mode == "R":
            print("Fetching reference data...")
            create_ref_data(BAZAAR_API_URL)
            print("Data exported to bazaar_ref.json")
            time.sleep(1)
            
            if input("Export to txt files? [Y/N]: ").upper() == "Y":
                export_ref_data_txt()
                print("Done.")
            time.sleep(1)

        elif mode == "C":
            print("Fetching comparison data...")
            create_comp_data(BAZAAR_API_URL)
            print("Data exported to bazaar_comp.json")
            time.sleep(1)

            if input("Export to txt files? [Y/N]: ").upper() == "Y":
                export_comp_data_txt()
                print("Done.")
            time.sleep(1)

        elif mode == "A":
            print("Automatic mode started. Press Ctrl+C to stop.")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping automatic mode.")

        elif mode == "Q":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
