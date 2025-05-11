import sys
import random
import hashlib
import os
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QMessageBox, QStackedWidget, QDialog, QSlider,
                            QColorDialog, QSpinBox, QFormLayout, QComboBox, QFrame,
                            QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor, QFont

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
ARR_SIZE = 100
RECT_WIDTH = 10
LOGIN_WIDTH = 500
LOGIN_HEIGHT = 400

class UserSystem:
    def __init__(self):
        self.users_file = "users.csv"
        self.users_df = self.load_users()
        
    def load_users(self):
        if os.path.exists(self.users_file):
            return pd.read_csv(self.users_file)
        return pd.DataFrame(columns=['username', 'password_hash'])
    
    def save_users(self):
        self.users_df.to_csv(self.users_file, index=False)
    
    def register_user(self, username, password):
        if username in self.users_df['username'].values:
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        new_user = pd.DataFrame({'username': [username], 'password_hash': [hashed]})
        self.users_df = pd.concat([self.users_df, new_user], ignore_index=True)
        self.save_users()
        return True
    
    def verify_user(self, username, password):
        if username not in self.users_df['username'].values:
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return self.users_df.loc[self.users_df['username'] == username, 'password_hash'].iloc[0] == hashed

class LoggingSystem:
    def __init__(self):
        self.comparison_logs_file = "comparison_logs.csv"
        self.performance_logs_file = "performance_logs.csv"
        self.comparison_logs_df = self.load_comparison_logs()
        self.performance_logs_df = self.load_performance_logs()
    
    def load_comparison_logs(self):
        if os.path.exists(self.comparison_logs_file):
            return pd.read_csv(self.comparison_logs_file)
        return pd.DataFrame(columns=[
            'timestamp', 'username', 'left_algorithm', 'right_algorithm',
            'array_size', 'winner'
        ])
    
    def load_performance_logs(self):
        if os.path.exists(self.performance_logs_file):
            return pd.read_csv(self.performance_logs_file)
        return pd.DataFrame(columns=[
            'timestamp', 'username', 'algorithm', 'execution_time_ms',
            'array_size', 'array_data'
        ])
    
    def save_logs(self):
        self.comparison_logs_df.to_csv(self.comparison_logs_file, index=False)
        self.performance_logs_df.to_csv(self.performance_logs_file, index=False)
    
    def add_log(self, username, left_algo, right_algo, time1, time2, array_data):
        # Add to comparison logs
        comparison_entry = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'username': [username],
            'left_algorithm': [left_algo],
            'right_algorithm': [right_algo],
            'array_size': [len(array_data)],
            'winner': [left_algo if time1 < time2 else right_algo]
        })
        self.comparison_logs_df = pd.concat([self.comparison_logs_df, comparison_entry], ignore_index=True)
        
        # Add to performance logs
        performance_entries = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 2,
            'username': [username] * 2,
            'algorithm': [left_algo, right_algo],
            'execution_time_ms': [time1, time2],
            'array_size': [len(array_data)] * 2,
            'array_data': [str(array_data)] * 2
        })
        self.performance_logs_df = pd.concat([self.performance_logs_df, performance_entries], ignore_index=True)
        
        self.save_logs()
    
    def get_comparison_stats(self):
        """Get statistics about algorithm comparisons"""
        if self.comparison_logs_df.empty:
            return "No comparison data available"
        
        stats = []
        stats.append("Comparison Statistics:")
        stats.append(f"Total comparisons: {len(self.comparison_logs_df)}")
        
        # Count wins for each algorithm
        wins = self.comparison_logs_df['winner'].value_counts()
        stats.append("\nAlgorithm Win Counts:")
        for algo, count in wins.items():
            stats.append(f"{algo}: {count} wins")
        
        return "\n".join(stats)
    
    def get_performance_stats(self):
        """Get statistics about algorithm performance"""
        if self.performance_logs_df.empty:
            return "No performance data available"
        
        stats = []
        stats.append("Performance Statistics:")
        
        # Group by algorithm and calculate statistics
        algo_stats = self.performance_logs_df.groupby('algorithm')['execution_time_ms'].agg(['mean', 'min', 'max', 'count'])
        stats.append("\nAlgorithm Performance (in milliseconds):")
        for algo, row in algo_stats.iterrows():
            stats.append(f"\n{algo}:")
            stats.append(f"  Average time: {row['mean']:.2f}ms")
            stats.append(f"  Best time: {row['min']:.2f}ms")
            stats.append(f"  Worst time: {row['max']:.2f}ms")
            stats.append(f"  Total runs: {row['count']}")
        
        return "\n".join(stats)

class FeedbackSystem:
    def __init__(self):
        self.feedback_file = "user_feedback.csv"
        self.feedback_df = self.load_feedback()
    
    def load_feedback(self):
        if os.path.exists(self.feedback_file):
            return pd.read_csv(self.feedback_file)
        return pd.DataFrame(columns=['timestamp', 'username', 'message'])
    
    def save_feedback(self):
        self.feedback_df.to_csv(self.feedback_file, index=False)
    
    def add_feedback(self, username, message):
        feedback_entry = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'username': [username],
            'message': [message]
        })
        self.feedback_df = pd.concat([self.feedback_df, feedback_entry], ignore_index=True)
        self.save_feedback()

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.user_system = UserSystem()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Sorting Visualizer Login')
        self.setFixedSize(LOGIN_WIDTH, LOGIN_HEIGHT)
        
        # Main layout with margins and spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add margins
        layout.setSpacing(20)  # Add spacing between elements
        
        # Title with larger font and spacing
        title = QLabel('Sorting Visualizer Login')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet('color: #2c3e50; margin-bottom: 20px;')
        layout.addWidget(title)
        
        # Username input with label
        username_label = QLabel('Username:')
        username_label.setFont(QFont('Arial', 10))
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setStyleSheet('''
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        ''')
        layout.addWidget(self.username_input)
        
        # Password input with label
        password_label = QLabel('Password:')
        password_label.setFont(QFont('Arial', 10))
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet('''
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        ''')
        layout.addWidget(self.password_input)
        
        # Add some spacing before buttons
        layout.addSpacing(20)
        
        # Buttons with styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        login_btn = QPushButton('Login')
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        login_btn.clicked.connect(self.handle_login)
        button_layout.addWidget(login_btn)
        
        register_btn = QPushButton('Register')
        register_btn.setStyleSheet('''
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        ''')
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        layout.addLayout(button_layout)
        
        # Center the widget in the window
        self.setLayout(layout)
        
        # Center the login window relative to the main window
        self.center_on_main_window()
    
    def center_on_main_window(self):
        # Get the main window's geometry
        main_geometry = self.main_window.geometry()
        
        # Calculate the center position relative to the main window
        x = main_geometry.x() + (main_geometry.width() - self.width()) // 2
        y = main_geometry.y() + (main_geometry.height() - self.height()) // 2
        
        # Move the window
        self.move(x, y)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
            
        if self.user_system.verify_user(username, password):
            self.main_window.current_user = username
            self.main_window.show_sorting_visualizer()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')
    
    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
            
        if len(username) < 3 or len(password) < 3:
            QMessageBox.warning(self, 'Error', 'Username/password too short (min 3 chars)')
            return
            
        if self.user_system.register_user(username, password):
            QMessageBox.information(self, 'Success', 'Registration successful!')
        else:
            QMessageBox.warning(self, 'Error', 'Username already exists')

class Settings:
    def __init__(self, username=None):
        self.username = username
        self.default_color = QColor(170, 183, 184)  # Default bar color
        self.complete_color = QColor(100, 180, 100)  # Color when sorting is complete
        self.animation_speed = 1  # Speed multiplier (1-10)
        self.settings_file = "user_settings.csv"
        self.settings_df = self.load_settings()
        self.load_user_settings()
        
    def load_settings(self):
        if os.path.exists(self.settings_file):
            return pd.read_csv(self.settings_file)
        return pd.DataFrame(columns=['username', 'default_color', 'complete_color', 'animation_speed'])
    
    def save_settings(self):
        try:
            # Update or add settings for current user
            if self.username:
                # Check if user settings exist
                user_mask = self.settings_df['username'] == self.username
                if user_mask.any():
                    # Update existing settings
                    self.settings_df.loc[user_mask, 'default_color'] = self.default_color.name()
                    self.settings_df.loc[user_mask, 'complete_color'] = self.complete_color.name()
                    self.settings_df.loc[user_mask, 'animation_speed'] = self.animation_speed
                else:
                    # Add new user settings
                    new_settings = pd.DataFrame({
                        'username': [self.username],
                        'default_color': [self.default_color.name()],
                        'complete_color': [self.complete_color.name()],
                        'animation_speed': [self.animation_speed]
                    })
                    self.settings_df = pd.concat([self.settings_df, new_settings], ignore_index=True)
            
            # Save all settings
            self.settings_df.to_csv(self.settings_file, index=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_user_settings(self):
        try:
            if self.username and not self.settings_df.empty:
                user_settings = self.settings_df[self.settings_df['username'] == self.username]
                if not user_settings.empty:
                    self.default_color = QColor(user_settings['default_color'].iloc[0])
                    self.complete_color = QColor(user_settings['complete_color'].iloc[0])
                    self.animation_speed = int(user_settings['animation_speed'].iloc[0])
                else:
                    # Reset to defaults if no settings found for user
                    self.default_color = QColor(170, 183, 184)
                    self.complete_color = QColor(100, 180, 100)
                    self.animation_speed = 1
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Use defaults if there's an error
            self.default_color = QColor(170, 183, 184)
            self.complete_color = QColor(100, 180, 100)
            self.animation_speed = 1

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Customization Settings')
        layout = QFormLayout()
        
        # Default color picker
        self.default_color_btn = QPushButton()
        self.default_color_btn.setStyleSheet(f"background-color: {self.settings.default_color.name()}")
        self.default_color_btn.clicked.connect(lambda: self.pick_color('default'))
        layout.addRow('Default Bar Color:', self.default_color_btn)
        
        # Complete color picker
        self.complete_color_btn = QPushButton()
        self.complete_color_btn.setStyleSheet(f"background-color: {self.settings.complete_color.name()}")
        self.complete_color_btn.clicked.connect(lambda: self.pick_color('complete'))
        layout.addRow('Complete Color:', self.complete_color_btn)
        
        # Speed slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(self.settings.animation_speed)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        # Speed value label
        self.speed_label = QLabel(f"Speed: {self.settings.animation_speed}x")
        layout.addRow('Animation Speed:', self.speed_slider)
        layout.addRow('', self.speed_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_and_close)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow('', button_layout)
        
        self.setLayout(layout)
    
    def pick_color(self, color_type):
        color = QColorDialog.getColor()
        if color.isValid():
            if color_type == 'default':
                self.settings.default_color = color
                self.default_color_btn.setStyleSheet(f"background-color: {color.name()}")
            else:
                self.settings.complete_color = color
                self.complete_color_btn.setStyleSheet(f"background-color: {color.name()}")
    
    def update_speed(self, value):
        self.settings.animation_speed = value
        self.speed_label.setText(f"Speed: {value}x")
    
    def save_and_close(self):
        self.settings.save_settings()
        self.accept()

class FeedbackDialog(QDialog):
    def __init__(self, feedback_system, username, parent=None):
        super().__init__(parent)
        self.feedback_system = feedback_system
        self.username = username
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Submit Feedback')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Submit Your Feedback')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet('color: #2c3e50; margin-bottom: 20px;')
        layout.addWidget(title)
        
        # Feedback message
        message_label = QLabel('Your Feedback:')
        message_label.setFont(QFont('Arial', 10))
        layout.addWidget(message_label)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText('Enter your feedback here...')
        self.message_input.setStyleSheet('''
            QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        ''')
        layout.addWidget(self.message_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        submit_btn.clicked.connect(self.submit_feedback)
        button_layout.addWidget(submit_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        ''')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def submit_feedback(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, 'Error', 'Please enter your feedback message')
            return
        
        self.feedback_system.add_feedback(self.username, message)
        QMessageBox.information(self, 'Success', 'Thank you for your feedback!')
        self.accept()

class SortingAlgorithms:
    def __init__(self):
        self.algorithms_file = "sorting_algorithms.csv"
        self.algorithms_df = self.load_algorithms()
        if self.algorithms_df.empty:
            self.initialize_algorithms()
    
    def load_algorithms(self):
        if os.path.exists(self.algorithms_file):
            return pd.read_csv(self.algorithms_file)
        return pd.DataFrame(columns=['AlgorithmID', 'Name', 'Description', 'TimeComplexity', 'SpaceComplexity'])
    
    def save_algorithms(self):
        self.algorithms_df.to_csv(self.algorithms_file, index=False)
    
    def initialize_algorithms(self):
        algorithms_data = {
            'AlgorithmID': [1, 2, 3, 4, 5, 6],
            'Name': [
                'Bubble Sort',
                'Selection Sort',
                'Insertion Sort',
                'Quick Sort',
                'Merge Sort',
                'Heap Sort'
            ],
            'Description': [
                'Repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.',
                'Divides the input into a sorted and unsorted region, and iteratively shrinks the unsorted region by extracting the smallest element.',
                'Builds the final sorted array one item at a time by comparing each item with the already sorted portion and inserting it at the correct position.',
                'Uses a divide-and-conquer strategy, picking a pivot element and partitioning the array around it.',
                'Divides the array into halves, recursively sorts them, and then merges the sorted halves.',
                'Uses a binary heap data structure to sort elements, converting the array into a max heap and repeatedly extracting the maximum.'
            ],
            'TimeComplexity': [
                'O(n²)',
                'O(n²)',
                'O(n²)',
                'O(n log n) average, O(n²) worst',
                'O(n log n)',
                'O(n log n)'
            ],
            'SpaceComplexity': [
                'O(1)',
                'O(1)',
                'O(1)',
                'O(log n)',
                'O(n)',
                'O(1)'
            ]
        }
        self.algorithms_df = pd.DataFrame(algorithms_data)
        self.save_algorithms()
    
    def get_algorithm_details(self, algorithm_name):
        algorithm = self.algorithms_df[self.algorithms_df['Name'] == algorithm_name]
        if not algorithm.empty:
            return algorithm.iloc[0]
        return None

class ResultsDialog(QDialog):
    def __init__(self, left_algo_name, right_algo_name, time1, time2, algorithms, parent=None):
        super().__init__(parent)
        self.left_algo_name = left_algo_name
        self.right_algo_name = right_algo_name
        self.time1 = time1
        self.time2 = time2
        self.algorithms = algorithms
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Sorting Comparison Results')
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Comparison Results')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet('color: #2c3e50; margin-bottom: 20px;')
        layout.addWidget(title)
        
        # Create a scrollable area for the results
        scroll = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Get algorithm details
        left_algo_details = self.algorithms.get_algorithm_details(self.left_algo_name)
        right_algo_details = self.algorithms.get_algorithm_details(self.right_algo_name)
        
        # Left algorithm details
        left_group = QFrame()
        left_group.setFrameStyle(QFrame.StyledPanel)
        left_group.setStyleSheet('''
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        ''')
        left_layout = QVBoxLayout()
        
        left_title = QLabel(self.left_algo_name)
        left_title.setFont(QFont('Arial', 14, QFont.Bold))
        left_title.setStyleSheet('color: #2c3e50;')
        left_layout.addWidget(left_title)
        
        left_details = QLabel(f"""
        Execution Time: {self.time1}ms
        Time Complexity: {left_algo_details['TimeComplexity']}
        Space Complexity: {left_algo_details['SpaceComplexity']}
        
        Description:
        {left_algo_details['Description']}
        """)
        left_details.setWordWrap(True)
        left_layout.addWidget(left_details)
        left_group.setLayout(left_layout)
        scroll_layout.addWidget(left_group)
        
        # Right algorithm details
        right_group = QFrame()
        right_group.setFrameStyle(QFrame.StyledPanel)
        right_group.setStyleSheet('''
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        ''')
        right_layout = QVBoxLayout()
        
        right_title = QLabel(self.right_algo_name)
        right_title.setFont(QFont('Arial', 14, QFont.Bold))
        right_title.setStyleSheet('color: #2c3e50;')
        right_layout.addWidget(right_title)
        
        right_details = QLabel(f"""
        Execution Time: {self.time2}ms
        Time Complexity: {right_algo_details['TimeComplexity']}
        Space Complexity: {right_algo_details['SpaceComplexity']}
        
        Description:
        {right_algo_details['Description']}
        """)
        right_details.setWordWrap(True)
        right_layout.addWidget(right_details)
        right_group.setLayout(right_layout)
        scroll_layout.addWidget(right_group)
        
        # Winner section
        winner_group = QFrame()
        winner_group.setFrameStyle(QFrame.StyledPanel)
        winner_group.setStyleSheet('''
            QFrame {
                background-color: #e8f5e9;
                border-radius: 10px;
                padding: 15px;
            }
        ''')
        winner_layout = QVBoxLayout()
        
        winner_title = QLabel('Winner')
        winner_title.setFont(QFont('Arial', 14, QFont.Bold))
        winner_title.setStyleSheet('color: #2c3e50;')
        winner_layout.addWidget(winner_title)
        
        winner = self.left_algo_name if self.time1 < self.time2 else self.right_algo_name
        time_diff = abs(self.time1 - self.time2)
        winner_details = QLabel(f"""
        {winner} was faster by {time_diff}ms
        """)
        winner_details.setWordWrap(True)
        winner_layout.addWidget(winner_details)
        winner_group.setLayout(winner_layout)
        scroll_layout.addWidget(winner_group)
        
        scroll.setLayout(scroll_layout)
        
        # Add scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class SortingVisualizer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.arr1 = [0] * ARR_SIZE
        self.arr2 = [0] * ARR_SIZE
        self.Barr = [0] * ARR_SIZE
        self.complete1 = False
        self.complete2 = False
        self.current_algo1 = None
        self.current_algo2 = None
        self.settings = Settings(self.main_window.current_user)
        self.logger = LoggingSystem()
        self.feedback_system = FeedbackSystem()
        self.algorithms = SortingAlgorithms()  # Initialize algorithms database
        self.completion_message = ""
        self.start_time = None
        self.left_algo_name = None
        self.right_algo_name = None
        self.time1 = None
        self.time2 = None
        self.running_second = False
        
        # Define algorithm map
        self.algo_map = {
            'Bubble Sort': lambda arr: self.bubble_sort(arr),
            'Selection Sort': lambda arr: self.selection_sort(arr),
            'Insertion Sort': lambda arr: self.insertion_sort(arr),
            'Quick Sort': lambda arr: self.quick_sort(arr),
            'Merge Sort': lambda arr: self.merge_sort(arr),
            'Heap Sort': lambda arr: self.heap_sort(arr)
        }
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Sorting Visualizer')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        layout = QVBoxLayout()
        
        # Menu bar
        menu_layout = QHBoxLayout()
        
        algorithms = [
            ('Merge Sort', self.merge_sort),
            ('Quick Sort', self.quick_sort),
            ('Bubble Sort', self.bubble_sort),
            ('Insertion Sort', self.insertion_sort),
            ('Selection Sort', self.selection_sort),
            ('Heap Sort', self.heap_sort)
        ]
        
        # Algorithm selection for left side
        self.left_algo_combo = QComboBox()
        for name, _ in algorithms:
            self.left_algo_combo.addItem(name)
        menu_layout.addWidget(QLabel('Left Algorithm:'))
        menu_layout.addWidget(self.left_algo_combo)
        
        # Algorithm selection for right side
        self.right_algo_combo = QComboBox()
        for name, _ in algorithms:
            self.right_algo_combo.addItem(name)
        menu_layout.addWidget(QLabel('Right Algorithm:'))
        menu_layout.addWidget(self.right_algo_combo)
        
        # Start comparison button
        compare_btn = QPushButton('Start Comparison')
        compare_btn.clicked.connect(self.start_comparison)
        menu_layout.addWidget(compare_btn)
        
        randomize_btn = QPushButton('Randomize')
        randomize_btn.clicked.connect(self.randomize_array)
        menu_layout.addWidget(randomize_btn)
        
        settings_btn = QPushButton('Settings')
        settings_btn.clicked.connect(self.show_settings)
        menu_layout.addWidget(settings_btn)
        
        feedback_btn = QPushButton('Feedback')
        feedback_btn.setStyleSheet('''
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        ''')
        feedback_btn.clicked.connect(self.show_feedback)
        menu_layout.addWidget(feedback_btn)
        
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        menu_layout.addWidget(logout_btn)
        
        layout.addLayout(menu_layout)
        
        # Visualization area
        viz_layout = QHBoxLayout()
        
        # Left visualization
        left_viz = QVBoxLayout()
        self.visualization1 = VisualizationWidget(self, is_left=True)
        left_viz.addWidget(self.visualization1)
        left_label = QLabel('Left Algorithm')
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet('''
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        ''')
        left_viz.addWidget(left_label)
        viz_layout.addLayout(left_viz)
        
        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('''
            QFrame {
                background-color: #bdc3c7;
                width: 2px;
                margin: 10px;
            }
        ''')
        viz_layout.addWidget(separator)
        
        # Right visualization
        right_viz = QVBoxLayout()
        self.visualization2 = VisualizationWidget(self, is_left=False)
        right_viz.addWidget(self.visualization2)
        right_label = QLabel('Right Algorithm')
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setStyleSheet('''
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        ''')
        right_viz.addWidget(right_label)
        viz_layout.addLayout(right_viz)
        
        layout.addLayout(viz_layout)
        self.setLayout(layout)
        
        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        
        self.randomize_array()
    
    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            self.visualization1.update()
            self.visualization2.update()
    
    def randomize_array(self):
        self.Barr = [random.randint(10, WINDOW_HEIGHT-100) for _ in range(ARR_SIZE)]
        self.arr1 = self.Barr.copy()
        self.arr2 = self.Barr.copy()
        self.complete1 = False
        self.complete2 = False
        self.visualization1.update()
        self.visualization2.update()
        
    def start_comparison(self):
        # Get selected algorithms
        self.left_algo_name = self.left_algo_combo.currentText()
        self.right_algo_name = self.right_algo_combo.currentText()
        
        # Reset states
        self.arr1 = self.Barr.copy()
        self.arr2 = self.Barr.copy()
        self.complete1 = False
        self.complete2 = False
        self.completion_message = ""
        self.start_time = None
        self.time1 = None
        self.time2 = None
        self.running_second = False
        
        # Start first algorithm
        self.current_algo1 = self.algo_map[self.left_algo_name](self.arr1)
        self.current_algo2 = None
        self.timer.start(100 // self.settings.animation_speed)
    
    def update_visualization(self):
        if not self.start_time:
            self.start_time = QTime.currentTime()
            
        if self.current_algo1 or self.current_algo2:
            try:
                if self.current_algo1:
                    next(self.current_algo1)
                elif self.current_algo2:
                    next(self.current_algo2)
                
                # Update visualizations
                self.visualization1.update()
                self.visualization2.update()
                
            except StopIteration as e:
                current_time = QTime.currentTime()
                
                if self.current_algo1:
                    self.complete1 = True
                    self.current_algo1 = None
                    self.time1 = self.start_time.msecsTo(current_time)
                    # Start second algorithm
                    self.current_algo2 = self.algo_map[self.right_algo_name](self.arr2)
                    self.start_time = QTime.currentTime()  # Reset start time for second algorithm
                
                elif self.current_algo2:
                    self.complete2 = True
                    self.current_algo2 = None
                    self.time2 = self.start_time.msecsTo(current_time)
                    self.timer.stop()
                    
                    # Show results dialog
                    dialog = ResultsDialog(
                        self.left_algo_name,
                        self.right_algo_name,
                        self.time1,
                        self.time2,
                        self.algorithms,
                        self
                    )
                    dialog.exec_()
                    
                    # Log the comparison results
                    self.logger.add_log(
                        username=self.main_window.current_user,
                        left_algo=self.left_algo_name,
                        right_algo=self.right_algo_name,
                        time1=self.time1,
                        time2=self.time2,
                        array_data=self.Barr.copy()
                    )
                
                self.visualization1.update()
                self.visualization2.update()
                
        # If both algorithms are complete, show final results
        elif self.complete1 and self.complete2 and self.time1 and self.time2:
            # Show results dialog
            dialog = ResultsDialog(
                self.left_algo_name,
                self.right_algo_name,
                self.time1,
                self.time2,
                self.algorithms,
                self
            )
            dialog.exec_()
            self.visualization1.update()
            self.visualization2.update()
    
    def logout(self):
        # Save current settings before logout
        self.settings.save_settings()
        self.main_window.show_login()
        
    # Sorting algorithms
    def bubble_sort(self, arr):
        for i in range(ARR_SIZE-1):
            for j in range(ARR_SIZE-1-i):
                if arr[j+1] < arr[j]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    yield
    
    def selection_sort(self, arr):
        n = len(arr)
        for i in range(n):
            min_idx = i
            # Find minimum element in unsorted array
            for j in range(i + 1, n):
                # Show comparison
                if arr[j] < arr[min_idx]:
                    min_idx = j
                yield  # Yield after each comparison to show the process
            # Swap if minimum element is not at current position
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                yield  # Yield after each swap
    
    def insertion_sort(self, arr):
        for i in range(1, ARR_SIZE):
            key = arr[i]
            j = i-1
            while j >= 0 and arr[j] > key:
                arr[j+1] = arr[j]
                j -= 1
                yield
            arr[j+1] = key
            yield
    
    def quick_sort(self, arr):
        def partition(low, high):
            i = low - 1
            pivot = arr[high]
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    yield
            arr[i+1], arr[high] = arr[high], arr[i+1]
            return i + 1

        def quick_sort_helper(low, high):
            if low < high:
                pi = yield from partition(low, high)
                yield from quick_sort_helper(low, pi-1)
                yield from quick_sort_helper(pi+1, high)

        yield from quick_sort_helper(0, len(arr)-1)
    
    def merge_sort(self, arr):
        def merge(l, m, r):
            left = arr[l:m+1]
            right = arr[m+1:r+1]
            i = j = 0
            k = l
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    arr[k] = left[i]
                    i += 1
                else:
                    arr[k] = right[j]
                    j += 1
                k += 1
                yield

            while i < len(left):
                arr[k] = left[i]
                i += 1
                k += 1
                yield

            while j < len(right):
                arr[k] = right[j]
                j += 1
                k += 1
                yield

        def merge_sort_helper(l, r):
            if l < r:
                m = (l + r) // 2
                yield from merge_sort_helper(l, m)
                yield from merge_sort_helper(m + 1, r)
                yield from merge(l, m, r)

        yield from merge_sort_helper(0, len(arr)-1)
    
    def heap_sort(self, arr):
        def heapify(n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and arr[left] > arr[largest]:
                largest = left

            if right < n and arr[right] > arr[largest]:
                largest = right

            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                yield
                yield from heapify(n, largest)

        def build_heap():
            n = len(arr)
            for i in range(n//2 - 1, -1, -1):
                yield from heapify(n, i)

        n = len(arr)
        yield from build_heap()

        for i in range(n-1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            yield
            yield from heapify(i, 0)

    def show_feedback(self):
        dialog = FeedbackDialog(self.feedback_system, self.main_window.current_user, self)
        dialog.exec_()

class VisualizationWidget(QWidget):
    def __init__(self, parent, is_left=True):
        super().__init__(parent)
        self.parent = parent
        self.is_left = is_left
        self.setMinimumHeight(WINDOW_HEIGHT - 150)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate spacing to center the visualization
        total_width = ARR_SIZE * RECT_WIDTH
        start_x = (self.width() - total_width) // 2
        
        # Draw array elements
        arr = self.parent.arr1 if self.is_left else self.parent.arr2
        complete = self.parent.complete1 if self.is_left else self.parent.complete2
        
        for i, val in enumerate(arr):
            color = self.parent.settings.default_color
            if complete:
                color = self.parent.settings.complete_color
            
            painter.fillRect(
                start_x + (i * RECT_WIDTH),
                self.height() - val,
                RECT_WIDTH - 1,  # Add small gap between bars
                val,
                color
            )
        
        # Draw completion message if both algorithms are done
        if self.parent.complete1 and self.parent.complete2 and self.parent.completion_message:
            painter.setPen(Qt.black)
            painter.setFont(QFont('Arial', 10))
            
            # Create a text area for the comparison results
            text_rect = self.rect()
            text_rect.setHeight(self.height() - 20)  # Leave some margin at bottom
            text_rect.setY(10)  # Start from top with margin
            
            # Split the message into lines and draw each line
            lines = self.parent.completion_message.strip().split('\n')
            y_offset = 20  # Starting y position
            
            for line in lines:
                # Draw each line with proper spacing
                painter.drawText(
                    text_rect.x() + 10,  # Left margin
                    y_offset,
                    text_rect.width() - 20,  # Right margin
                    20,  # Line height
                    Qt.AlignLeft | Qt.AlignVCenter,
                    line.strip()
                )
                y_offset += 25  # Increase spacing between lines

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sorting Visualizer')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.current_user = None
        
        # Create stacked widget for switching between login and visualizer
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create and add windows
        self.login_window = LoginWindow(self)
        self.sorting_visualizer = None  # Will be created when needed
        
        self.stacked_widget.addWidget(self.login_window)
        
        # Show login window first
        self.show_login()
        
    def show_login(self):
        # Reset current user and destroy visualizer
        self.current_user = None
        if self.sorting_visualizer:
            self.stacked_widget.removeWidget(self.sorting_visualizer)
            self.sorting_visualizer.deleteLater()
            self.sorting_visualizer = None
        self.stacked_widget.setCurrentWidget(self.login_window)
        
    def show_sorting_visualizer(self):
        if not self.sorting_visualizer:
            self.sorting_visualizer = SortingVisualizer(self)
            self.stacked_widget.addWidget(self.sorting_visualizer)
        self.stacked_widget.setCurrentWidget(self.sorting_visualizer)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())