import requests
import json
import datetime
import os
from typing import List, Dict, Any

# Ensure necessary directories exist
DIRECTORIES = ['Bazaar', 'heure', 'benef', 'calculs', 'journalier', 'journalierJS', 'flip']
for directory in DIRECTORIES:
    os.makedirs(directory, exist_ok=True)

def get_bazaar_infos(api_url: str) -> List[Dict[str, Any]]:
    """
    Fetches real-time Bazaar data from the Hypixel API.
    
    Args:
        api_url (str): The URL of the Bazaar API.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing product information (id, sell price, buy price).
    """
    try:
        r = requests.get(api_url)
        r.raise_for_status()
        data = r.json()
        product_info_list = []
        for product_id, product_data in data["products"].items():
            product_info = {"product_id": product_id}
            quick_status = product_data.get("quick_status", {})
            product_info["sell_price"] = quick_status.get("sellPrice", None)
            product_info["buy_price"] = quick_status.get("buyPrice", None)
            product_info_list.append(product_info)
        return product_info_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bazaar info: {e}")
        return []

def get_player_infos(api_key: str, uuid: str) -> Dict[str, Any]:
    """
    Fetches player stats/achievements (specifically Skyblock levels) using the Hypixel API.
    
    Args:
        api_key (str): The Hypixel API key.
        uuid (str): The player's UUID.
        
    Returns:
        Dict[str, Any]: A dictionary of the player's Skyblock achievement levels.
    """
    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if "player" in data and data["player"] is not None:
            achievements = data["player"].get("achievements", {})
            player_info = {
                "skyblock_combat": achievements.get("skyblock_combat"),
                "skyblock_harvester": achievements.get("skyblock_harvester"),
                "skyblock_excavator": achievements.get("skyblock_excavator"),
                "skyblock_gatherer": achievements.get("skyblock_gatherer"),
                "skyblock_domesticator": achievements.get("skyblock_domesticator"),
                "skyblock_dungeoneer": achievements.get("skyblock_dungeoneer"),
                "skyblock_curator": achievements.get("skyblock_curator"),
                "skyblock_angler": achievements.get("skyblock_angler")
            }
        else:
            player_info = {}
        return player_info
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player info: {e}")
        return {}

def print_player_info(player_info: Dict[str, Any]):
    """
    Prints the player's Skyblock levels to the console.
    """
    print("\nPlayer Information (UUID based):")
    print(f"{player_info.get('skyblock_combat', 'N/A')} Combat Levels")
    print(f"{player_info.get('skyblock_harvester', 'N/A')} Farming Levels")
    print(f"{player_info.get('skyblock_excavator', 'N/A')} Mining Levels")
    print(f"{player_info.get('skyblock_gatherer', 'N/A')} Foraging Levels")
    print(f"{player_info.get('skyblock_domesticator', 'N/A')} Taming Levels")
    print(f"{player_info.get('skyblock_dungeoneer', 'N/A')} Dungeon Levels")
    print(f"{player_info.get('skyblock_curator', 'N/A')} Enchanting Levels")
    print(f"{player_info.get('skyblock_angler', 'N/A')} Fishing Levels")

def create_ref_data(api_url: str):
    """Creates the reference data file (bazaar_ref.json)."""
    bazaar_info = get_bazaar_infos(api_url)
    with open('bazaar_ref.json', 'w') as f:
        json.dump(bazaar_info, f)

def create_comp_data(api_url: str):
    """Creates the comparison data file (bazaar_comp.json)."""
    bazaar_info = get_bazaar_infos(api_url)
    with open('bazaar_comp.json', 'w') as f:
        json.dump(bazaar_info, f)

def aggregate_hourly_data():
    """Aggregates all hourly JSON files into a daily summary."""
    hourly_dir = 'heure'
    
    if not os.path.exists(hourly_dir):
        print(f"Directory '{hourly_dir}' not found.")
        return

    bazaar_files = [f for f in os.listdir(hourly_dir) if f.startswith('bazaar_') and f.endswith('.json')]
    if not bazaar_files:
        print(f"No 'bazaar_{{hour}}.json' files found in '{hourly_dir}'.")
        return

    bazaar_info_total = []
    for file in bazaar_files:
        file_path = os.path.join(hourly_dir, file)
        try:
            with open(file_path, 'r') as f:
                bazaar_info = json.load(f)
                bazaar_info_total.extend(bazaar_info)
        except json.JSONDecodeError:
            print(f"Error reading {file_path}")

    if not bazaar_info_total:
        print("No Bazaar info found in files.")
        return

    products = {}
    for product in bazaar_info_total:
        p_id = product['product_id']
        sell = product.get('sell_price', 0) or 0 # Handle None
        buy = product.get('buy_price', 0) or 0   # Handle None
        
        if p_id not in products:
            products[p_id] = {'sell_price': [], 'buy_price': []}
        products[p_id]['sell_price'].append(sell)
        products[p_id]['buy_price'].append(buy)

    bazaar_final = []
    for p_id, prices in products.items():
        avg_buy = sum(prices['buy_price']) / len(prices['buy_price']) if prices['buy_price'] else 0
        avg_sell = sum(prices['sell_price']) / len(prices['sell_price']) if prices['sell_price'] else 0
        bazaar_final.append({'product_id': p_id, 'sell_price': avg_sell, 'buy_price': avg_buy})

    today = datetime.date.today().strftime("%Y-%m-%d")
    final_file_path = os.path.join('Bazaar', f"bazaar_{today}.json")
    with open(final_file_path, 'w') as f:
        json.dump(bazaar_final, f)

def export_comp_data_txt():
    """Exports comparison data to a text file."""
    if not os.path.exists('bazaar_comp.json'):
         return
    with open('bazaar_comp.json', 'r') as f:
        bazaar_comp_data = json.load(f)
    with open('comp_data', 'w') as comp_file:
        for item in bazaar_comp_data:
            comp_file.write(f"{item['product_id']} {item['sell_price']} {item['buy_price']}\n")

def export_ref_data_txt():
    """Exports reference data to a text file."""
    if not os.path.exists('bazaar_ref.json'):
        return
    with open('bazaar_ref.json', 'r') as f:
        bazaar_ref_data = json.load(f)
    with open('ref_data', 'w') as ref_file:
        for item in bazaar_ref_data:
            ref_file.write(f"{item['product_id']} {item['sell_price']} {item['buy_price']}\n")

def calculate_daily_profit_averages(): 
    """Calculates daily averages and identifies profitable items."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    bazaar_dir = 'Bazaar'
    
    if not os.path.exists(bazaar_dir):
        return

    bazaar_files = [f for f in os.listdir(bazaar_dir) if f.startswith('bazaar_') and f.endswith('.json')]
    stats_per_item = {}

    for file in bazaar_files:
        with open(os.path.join(bazaar_dir, file), 'r') as f:
            data = json.load(f)
            for item in data:
                item_id = item['product_id']
                buy_price = item.get('buy_price', 0) or 0
                sell_price = item.get('sell_price', 0) or 0
                
                if item_id not in stats_per_item:
                    stats_per_item[item_id] = {'buy_price': [], 'sell_price': []}
                stats_per_item[item_id]['buy_price'].append(buy_price)
                stats_per_item[item_id]['sell_price'].append(sell_price)

    benef_dir = 'benef'
    benef_file_path = os.path.join(benef_dir, f'items_en_benef_{today}.txt')
    # Clear previous file content if needed, or append. Here assuming append as in original.

    for item_id, stats in stats_per_item.items():
        if not stats['buy_price'] or not stats['sell_price']:
            continue
            
        avg_buy = sum(stats['buy_price']) / len(stats['buy_price'])
        avg_sell = sum(stats['sell_price']) / len(stats['sell_price'])
        profit = avg_sell - avg_buy
        
        if profit > 0 and avg_buy != 0:
            with open(benef_file_path, 'a') as f:
                f.write(f"Profit of: {profit:.2f} on: {item_id}\n")

    data_json = {
        "date": today,
        "items": []
    }
    
    for item_id, stats in stats_per_item.items():
        if not stats['buy_price'] or not stats['sell_price']:
            continue

        avg_buy = sum(stats['buy_price']) / len(stats['buy_price'])
        avg_sell = sum(stats['sell_price']) / len(stats['sell_price'])
        
        data_json["items"].append({
            "item_id": item_id,
            "avg_buy": avg_buy,
            "avg_sell": avg_sell,
            "max_buy": max(stats['buy_price']),
            "min_buy": min(stats['buy_price']),
            "max_sell": max(stats['sell_price']),
            "min_sell": min(stats['sell_price']),
            "profit": avg_sell - avg_buy
        })

    output_dir = 'calculs'
    with open(os.path.join(output_dir, f'calculs_benefs_moyenne_{today}.json'), 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

def compare_buy_sell_prices():
    """Compares current buy prices with average sell prices to find flip opportunities."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    bazaar_file = os.path.join('Bazaar', f'bazaar_{today}.json')
    calc_file = os.path.join('calculs', f'calculs_benefs_moyenne_{today}.json')

    if not os.path.exists(bazaar_file) or not os.path.exists(calc_file):
        print(f"Missing data files for {today}.")
        return
    
    with open(bazaar_file, 'r') as f:
        bazaar_data = json.load(f)
        buy_prices = {item["product_id"]: item.get("buy_price", 0) for item in bazaar_data}

    with open(calc_file, 'r') as f:
        calc_data = json.load(f)
        # Handle key mismatch if json structure changed. Assuming 'items' key exists
        sell_prices = {item["item_id"]: item.get("avg_sell", 0) for item in calc_data.get("items", [])}

    profitable_items = []
    for item_id, buy_price in buy_prices.items():
        if buy_price == 0: continue
        
        sell_price = sell_prices.get(item_id, 0)
        if buy_price < sell_price:
            diff = sell_price - buy_price
            profitable_items.append({
                "item_id": item_id,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "difference": diff
            })
            
    js_file_path = os.path.join('journalierJS', 'data_js.js')
    content_js = f'const data = {json.dumps({"profitable_items": profitable_items}, indent=4)};'
    with open(js_file_path, 'w') as f:
        f.write(content_js)
    
    print(f"JS data saved to: {js_file_path}")

def update_flip_data(api_url: str):
    """Updates the flip data JS file with moving week info."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        bazaar_data = response.json()
    except Exception as e:
        print(f"Error updating flip data: {e}")
        return

    flip_file_path = os.path.join('flip', 'data_flip.js')
    
    # Load existing
    flips = {"flips": []}
    if os.path.exists(flip_file_path) and os.path.getsize(flip_file_path) > 0:
        with open(flip_file_path, 'r') as f:
            content = f.read().strip()
            if content.startswith('const data_flips = '):
                json_content = content[len('const data_flips = '):].strip().rstrip(';')
                try:
                    flips = json.loads(json_content)
                except json.JSONDecodeError:
                    pass

    # Update
    for flip_item in flips['flips']:
        p_id = flip_item['product_id']
        if p_id in bazaar_data['products']:
            qs = bazaar_data['products'][p_id]['quick_status']
            flip_item['buyMovingWeek'] = qs.get('buyMovingWeek', 0)
            flip_item['sellMovingWeek'] = qs.get('sellMovingWeek', 0)

    # Save
    with open(flip_file_path, 'w') as f:
        f.write('const data_flips = ')
        json.dump(flips, f, indent=4)
        f.write(';')
    
    print(f"Flip data updated in {flip_file_path}")

def record_hourly_data(api_url: str):
    """Records the current Bazaar data into an hourly JSON file."""
    current_hour = datetime.datetime.now().strftime("%H")
    filename = f"bazaar_{current_hour}.json"
    bazaar_info = get_bazaar_infos(api_url)
    
    file_path = os.path.join('heure', filename)
    with open(file_path, 'w') as f:
        json.dump(bazaar_info, f)

def run_automation_cycle(api_url: str, days_running: int):
    """Runs the full automation cycle."""
    aggregate_hourly_data() # Originally recup_data_comp_auto logic roughly
    record_hourly_data(api_url)
    calculate_daily_profit_averages()
    compare_buy_sell_prices()
    update_flip_data(api_url)
    print(f"Running for {days_running + 1} days.\n")
