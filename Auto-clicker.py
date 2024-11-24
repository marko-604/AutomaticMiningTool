import os
import sys
import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard  # Add this import
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QRect
import csv
from datetime import timedelta

num_clicks = 1
wallet = 100  # Initial money in the wallet
bet_amount = 1  # Bet amount per round
gains = 1.03  # Multiplier for winning
wins_count = 0


base_dir = "screenshots"
# Load gem and bomb images for matching
gem_img = cv2.imread('recog/jewel_gray.PNG', cv2.IMREAD_GRAYSCALE)
bomb_img = cv2.imread('recog/bomb_highlighted.png', cv2.IMREAD_GRAYSCALE)
bomb_img2 = cv2.imread('recog/a1.PNG', cv2.IMREAD_GRAYSCALE)
bomb_img3 = cv2.imread('recog/bomb_highlighted2.PNG', cv2.IMREAD_GRAYSCALE)
cashout_img = cv2.imread('recog/cashout.png', cv2.IMREAD_GRAYSCALE)
button_width, button_height = 240, 40

# Define positions and sizes
grid_start_x, grid_start_y = 600, 200
square_size = 100
spacing = 11
cashout_button_position = (212, 477)
cashout_clicking = ((212 + 240) // 2, (477 + 20))
bet_button_position = (212, 371)
bet_clicking = ((212 + 240) // 2, (371 + 20))

row_labels = ['A', 'B', 'C', 'D', 'E']
col_labels = ['1', '2', '3', '4', '5']

# Initialize CSV file with dynamic headers
csv_filename = "grid_results.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Create headers dynamically
    header = [f"Gem{i+1}" for i in range(num_clicks)] + ["Win"] + [f"Pos{i+1}" for i in range(num_clicks)]
    writer.writerow(header)


class TransparentOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iteration = 1  # Initialize iteration counter
        self.start_time = None  # To store the start time of the game
        self.elapsed_time = timedelta(0)  # To accumulate the total runtime
        self.overlay_visible = True
        self.game_running = False
        self.num_clicks = num_clicks  # Number of random squares to click

        # Set up the transparent overlay window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)  # Adjust to your screen resolution

        # Overlay toggle button
        self.overlay_button = QPushButton('Turn Overlay Off', self)
        self.overlay_button.setGeometry(50, 50, 150, 50)
        self.overlay_button.clicked.connect(self.toggle_overlay)
        self.overlay_button.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        # Game automation toggle button
        self.game_button = QPushButton('Start Game Automation', self)
        self.game_button.setGeometry(50, 110, 150, 50)
        self.game_button.clicked.connect(self.toggle_game)
        self.game_button.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        # Input button to adjust number of clicks
        self.num_clicks_button = QPushButton(f'Clicks: {self.num_clicks}', self)
        self.num_clicks_button.setGeometry(50, 170, 150, 50)
        self.num_clicks_button.clicked.connect(self.change_num_clicks)
        self.num_clicks_button.setStyleSheet("background-color: white; color: black; font-size: 14px;")


        # Timer for the game automation loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_game)

        # Start listening for the "Esc" key to stop the game automation
        keyboard.add_hotkey('esc', self.stop_game)

    def toggle_overlay(self):
        self.overlay_visible = not self.overlay_visible
        self.overlay_button.setText('Turn Overlay On' if not self.overlay_visible else 'Turn Overlay Off')
        self.update()

    def change_num_clicks(self):
        """
        Increase the number of clicks by 1, cycling back to 1 after reaching a maximum of 24 clicks.
        Dynamically updates the CSV headers to match the new number of clicks.
        """
        self.num_clicks = self.num_clicks + 1 if self.num_clicks < 24 else 1
        self.num_clicks_button.setText(f'Clicks: {self.num_clicks}')
        print(f"Number of clicks set to: {self.num_clicks}")

        # Dynamically reinitialize the CSV with updated headers
        csv_filename = "grid_results.csv"
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Create dynamic headers based on updated num_clicks
            header = [f"Gem{i + 1}" for i in range(self.num_clicks)] + ["Win"] + [f"Pos{i + 1}" for i in
                                                                                  range(self.num_clicks)]
            writer.writerow(header)
        print(f"CSV headers updated: {header}")
    def toggle_game(self):
        self.game_running = not self.game_running
        if self.game_running:
            print(f"Wallet Amount: {wallet}")
            self.game_button.setText('Stop Game Automation\n\t(esc)')
            self.timer.start(1000)  # Run the game every 1 second

            if self.start_time is None:
                self.start_time = time.time()
        else:
            print("Stopping game automation...")
            self.game_button.setText('Start Game Automation')
            self.timer.stop()

            if self.start_time:
                self.elapsed_time += timedelta(seconds=time.time() - self.start_time)
                self.start_time = None

            print(f"Total Runtime: {str(self.elapsed_time)}")

    def stop_game(self):
        if self.game_running:
            print("Game automation stopped by keyboard shortcut.")
            self.game_running = False
            self.game_button.setText('Start Game Automation')
            self.timer.stop()

            if self.start_time:
                self.elapsed_time += timedelta(seconds=time.time() - self.start_time)
                self.start_time = None

            print(f"Total Runtime: {str(self.elapsed_time)}")

    def run_game(self):
        global wallet, wins_count
        try:
            wallet -= bet_amount
            print(f"Wallet after bet: ${wallet}")
            # Click Bet button
            pyautogui.moveTo(bet_clicking[0], bet_clicking[1], duration=0.2)
            pyautogui.click()
            #print("Game Iteration:", self.iteration)

            # Place the bet and deduct the bet amount from the wallet
            time.sleep(1)

            # Generate grid positions and randomly select positions to click
            grid_positions = [
                (grid_start_x + col * (square_size + spacing) + square_size // 2,
                 grid_start_y + row * (square_size + spacing) + square_size // 2)
                for row in range(5) for col in range(5)
            ]

            classified_positions = []
            for idx, position in enumerate(grid_positions):
                row = idx // 5  # Determine row index
                col = idx % 5  # Determine column index
                label = f"{row_labels[row]}{col_labels[col]}"
                classified_positions.append((label, position))

            selected_positions = random.sample(grid_positions, self.num_clicks)

            # Collect all rows of data for this game
            row_data = [0] * self.num_clicks  # Default 0 for bomb
            positions = [""] * self.num_clicks  # To track the positions
            all_row_data = []

            for idx, position in enumerate(selected_positions):
                label, _ = next(
                    ((row_label + col_label, pos) for row_label, col_label, pos in [
                        (row_labels[idx // 5], col_labels[idx % 5], pos)
                        for idx, pos in enumerate(grid_positions)
                    ] if pos == position),
                    (None, None)
                )

                pyautogui.moveTo(position[0], position[1], duration=0.2)
                pyautogui.click()
                time.sleep(1)

                # Define the region for the screenshot
                region = (
                    position[0] - square_size // 2,
                    position[1] - square_size // 2,
                    square_size,
                    square_size
                )

                screenshot = pyautogui.screenshot(region=region)
                screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

                iteration_dir = os.path.join(base_dir, str(self.iteration))
                os.makedirs(iteration_dir, exist_ok=True)
                filename = os.path.join(iteration_dir, f"{label}.png")
                cv2.imwrite(filename, screen_img)

                # Check for gem or bomb
                if self.is_gem(screen_img):
                    row_data[idx] = 1  # Gem found
                elif self.is_bomb(screen_img):
                    row_data[idx] = 0  # Bomb found
                    break  # Stop further clicks if a bomb is found

                positions[idx] = label

            # If a bomb was encountered, fill the remaining positions with '9'
            if 0 in row_data:
                row_data = [9 if x == 0 else x for x in row_data]

            # Determine win condition (any 1 means win)
            win_condition = 1 if all(value == 1 for value in row_data) else 0

            # Write the result to the CSV
            with open(csv_filename, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(row_data + [win_condition] + positions)
            if(win_condition==1):
                wins_count += 1
                wallet += bet_amount * gains  # Add the winnings to the wallet
                print(f"Win! Total Wins: {wins_count}. Total: {self.iteration} win%: {wins_count/self.iteration *100}% Wallet: ${wallet}")
            #print("Data written to CSV successfully.")
            # Click Cashout button
            pyautogui.moveTo(cashout_clicking[0], cashout_clicking[1], duration=0.2)

            pyautogui.click()

            self.iteration += 1

        except Exception as e:
            print(f"Error in run_game: {e}")

    def is_gem(self, screen_img):
        """
        Check if the image contains a gem.
        """
        gem_result = cv2.matchTemplate(screen_img, gem_img, cv2.TM_CCOEFF_NORMED)

        return np.max(gem_result) > 0.65

    def is_bomb(self, screen_img):
        """
        Check if the image contains a bomb.
        """
        bomb_result = cv2.matchTemplate(screen_img, (bomb_img or bomb_img2 or bomb_img3), cv2.TM_CCOEFF_NORMED)
        return np.max(bomb_result) > 0.65

    def paintEvent(self, event):
        if not self.overlay_visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the 5x5 grid in red
        pen = QPen(QColor(255, 0, 0, 150), 2)  # 150 alpha for semi-transparency
        painter.setPen(pen)
        for row in range(5):
            for col in range(5):
                top_left_x = grid_start_x + col * (square_size + spacing)
                top_left_y = grid_start_y + row * (square_size + spacing)
                painter.drawRect(top_left_x, top_left_y, square_size, square_size)

        # Draw the Cashout button overlay in red
        pen.setColor(QColor(255, 0, 0, 150))
        painter.setPen(pen)
        painter.drawRect(cashout_button_position[0], cashout_button_position[1], button_width, button_height)

        # Draw text in the middle of the Cashout button
        text = "Cashout"
        font = QFont("Arial", 12)  # Customize font style and size
        painter.setFont(font)
        text_rect = QRect(
            cashout_button_position[0],
            cashout_button_position[1],
            button_width,
            button_height
        )
        painter.drawText(text_rect, Qt.AlignCenter, text)

        # Draw the Bet button overlay in red
        painter.setPen(pen)
        painter.drawRect(bet_button_position[0], bet_button_position[1], button_width, button_height)

        # Draw text in the middle of the Bet button
        text = "Bet"
        text_rect = QRect(
            bet_button_position[0],
            bet_button_position[1],
            button_width,
            button_height
        )
        painter.drawText(text_rect, Qt.AlignCenter, text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentOverlay()
    window.show()
    sys.exit(app.exec_())
