import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

wallet = 100
bet = 1
wining_amt = 1.48

# Read the data into a DataFrame
data = "grid_results.csv"
try:
    df = pd.read_csv(data, sep=',')

    # Dynamically identify the "Gem" and other required columns
    gem_columns = [col for col in df.columns if col.startswith("Gem")]
    position_column = "Position"
    required_columns = gem_columns + ["Win", position_column]

    # Validate required columns
    if not all(col in df.columns for col in required_columns):
        print(f"Error: Missing required columns. Ensure the file contains {required_columns}.")
        exit()

    # Filter the DataFrame to include only required columns
    df = df[required_columns]

except FileNotFoundError:
    print("Error: File not found. Ensure the path to 'grid_results.csv' is correct.")
    exit()

# Initialize a 5x5 grid for counting positions
grid_labels = [f"{chr(65+i)}{j}" for i in range(5) for j in range(1, 6)]
grid = {label: 0 for label in grid_labels}

# Initialize counters for wins, losses, and total rows
win_count = 0
loss_count = 0
total_rows = len(df)

# Iterate over the rows
for idx, row in df.iterrows():
    try:
        # Check if it's a win
        win = str(row["Win"]).strip()
        if win and win.upper() not in ["0", "N"]:  # It's a win
            win_count += 1
            # Process positions from the Position column
            positions = str(row[position_column]).strip()
            if positions:  # Ensure it's not empty
                positions = positions.split(",")
                for position in positions:
                    position = position.strip().upper()  # Clean and format the position
                    if position in grid:  # Validate position against the grid
                        grid[position] += 1
                    else:
                        print(f"Warning: Invalid position '{position}' in row {idx}. Skipping...")
            else:
                print(f"Warning: Missing positions in row {idx}. Skipping...")

        else:  # It's a loss
            loss_count += 1
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        print(f"Row content: {row}")
        continue



# Print the statistics
print(f"Total Rows Processed: {total_rows}")
print(f"Total Wins: {win_count}")
print(f"Total Losses: {loss_count}")



net = (win_count * wining_amt) - (bet * loss_count)
wallet_net = wallet + net
print(f"Total Winning Amount: {win_count * wining_amt}")
print(f"\nNet Change: {net}")

# Convert the grid dictionary to a 5x5 matrix for the heatmap
heatmap_data = np.array([grid[f"{chr(65+i)}{j}"] for i in range(5) for j in range(1, 6)]).reshape(5, 5)

# Generate the heatmap
plt.figure(figsize=(8, 6))
plt.title("Heatmap of Winning Positions")
plt.imshow(heatmap_data, cmap="Greens", origin="upper")  # Use the "Greens" colormap
plt.colorbar(label="Count of Wins")

# Set the X-axis to be the numbered columns (1-5)
plt.xticks(ticks=np.arange(5), labels=[f"{i+1}" for i in range(5)])

# Set the Y-axis to be the lettered rows (A-E)
plt.yticks(ticks=np.arange(5), labels=[chr(65+i) for i in range(5)])

plt.xlabel("Column")
plt.ylabel("Row")
plt.show()
