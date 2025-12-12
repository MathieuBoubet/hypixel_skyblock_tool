# Hypixel Skyblock Bazaar Tool

A professional, automated tool for tracking Hypixel Skyblock Bazaar prices, identifying flip opportunities, and analyzing player stats.

## Features

- **Real-time Bazaar Tracking**: Fetches and records Bazaar data hourly.
- **Flip Analysis**: Automatically compares buy and sell prices to identify profitable flips.
- **Player Inspection**: View detailed Skyblock skill levels for any player.
- **Data Export**: Exports data to JSON and TXT formats for external analysis.
- **Automated Mode**: Runs in the background to continuously track market trends.

## Prerequisites

- Python 3.8+
- A [Hypixel API Key](https://developer.hypixel.net/)

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/MathieuBoubet/hypixel-skyblock-tool.git
    cd hypixel-skyblock-tool
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**
    This project uses environment variables for security.
    
    - Copy the example environment file:
      ```bash
      cp .env.example .env
      # On Windows CMD: copy .env.example .env
      ```
    - Open `.env` and paste your Hypixel API Key:
      ```ini
      HYPIXEL_API_KEY=your_actual_api_key_here
      ```

## Usage

Run the main script:
```bash
python main.py
```

### Menu Options
- **[I] Inspect Player Stats**: Enter a username to see their Skyblock skill levels.
- **[R] Update Reference Prices**: Fetch current prices to set a baseline.
- **[C] Update Comparison Prices**: Fetch current prices to compare against the baseline.
- **[A] Automatic Mode**: Starts the hourly tracking and flip analysis cycle. Press `Ctrl+C` to stop.
- **[Q] Quit**: Exit the application.

## Project Structure

- `main.py`: Entry point and user interface.
- `definitions.py`: Core logic for API interaction, data processing, and file management.
- `Bazaar/`, `heure/`, `benef/`: Data directories generated automatically during runtime.

## License

[MIT](https://choosealicense.com/licenses/mit/)
