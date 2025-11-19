REAL TIME CLIMATE DATA STREAM SIMULATOR >>

This project simulates a real-time data stream using historical climate data.
It generates new timestamped readings for:

>Temperature
>Humidity
>Air Quality (AQI)

The simulated output behaves realistically by incorporating trend, seasonal patterns, and noise learned from the historical dataset.

📁 Project Structure :
.
├── simulate_stream.py      # Main simulation engine
├── historical.csv          # Input sample dataset (48 rows, 2 days)
└── simulated_stream.csv    # Output (auto-generated)

⚙️ How It Works:

1. Load Historical Data
The script reads historical.csv (your 2-day climate dataset).

2. Analyze Patterns
The system extracts:
Mean & standard deviation for each variable
Trend (average change between consecutive rows)
Hourly seasonal behavior
Typical timestamp interval

3. Generate Future Values
Every new reading is calculated using:
>Previous value
>Trend continuation
>Hourly seasonal adjustment
>Small random noise for realism
>Value clamping

4. Stream the Data
A new row is appended to simulated_stream.csv at a constant interval (e.g., every 1 second).




🚀 Running the Simulation

Open CMD or terminal in the project folder and run >

"python simulate_stream.py --history historical.csv --out simulated_stream.csv --interval 1.0 --method trend_seasonal"

Parameters Explained:
 --history >  Input dataset (historical CSV file)               
--out >  Output file where simulated rows will be appended 
--interval > Seconds between each generated data point         
--method >  Simulation style 
 
📊 Input Dataset Example (historical.csv)

The historical dataset contains these columns:
>timestamp
>temperature
>humidity
>air_quality
48 rows covering the last 2 days.
The simulator learns from this dataset and generates future sensor-like data that follows similar behavior.

📄 Output (simulated_stream.csv) :

Every second (based on your interval), a new row like this is appended:

timestamp,temperature,humidity,air_quality
2025-01-12T14:05:21,29.38,61.72,42.15

🧹 Stopping the Simulation
The file grows continuously until you stop the script (Ctrl + C).


🛠️ Requirements :
>Python 3.8+
>pandas
>numpy


🧱 Features
✔ Trend-based simulation
✔ Hourly seasonal modeling
✔ Noise injection for realistic randomness
✔ Timestamps auto-incremented
✔ Real-time or history-based mode
✔ CSV streaming output


📝 Author
> PRANEET A K
Climate Data Stream Simulation Project
2025

