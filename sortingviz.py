import sys
import random
import hashlib
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QMessageBox, QStackedWidget, QDialog, QSlider,
                            QColorDialog, QSpinBox, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
ARR_SIZE = 150
RECT_WIDTH = 8
LOGIN_WIDTH = 500
LOGIN_HEIGHT = 400

class UserSystem:
    def __init__(self):
        self.users_file = "users.json"
        self.users = self.load_users()
        
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)
    
    def register_user(self, username, password):
        if username in self.users:
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = hashed
        self.save_users()
        return True
    
    def verify_user(self, username, password):
        if username not in self.users:
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return self.users[username] == hashed

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.user_system = UserSystem()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Sorting Visualizer Login')
        self.setFixedSize(LOGIN_WIDTH, LOGIN_HEIGHT)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Sorting Visualizer Login')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16))
        layout.addWidget(title)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.handle_login)
        button_layout.addWidget(login_btn)
        
        register_btn = QPushButton('Register')
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
            
        if self.user_system.verify_user(username, password):
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
    def __init__(self):
        self.default_color = QColor(170, 183, 184)  # Default bar color
        self.complete_color = QColor(100, 180, 100)  # Color when sorting is complete
        self.animation_speed = 1  # Speed multiplier (1-10)
        
    def save_settings(self):
        settings = {
            'default_color': self.default_color.name(),
            'complete_color': self.complete_color.name(),
            'animation_speed': self.animation_speed
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.default_color = QColor(settings['default_color'])
                self.complete_color = QColor(settings['complete_color'])
                self.animation_speed = settings['animation_speed']
        except:
            pass  # Use defaults if file doesn't exist

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
        layout.addRow('Animation Speed:', self.speed_slider)
        
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
    
    def save_and_close(self):
        self.settings.save_settings()
        self.accept()

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
        self.settings = Settings()
        self.settings.load_settings()
        self.completion_message = ""
        self.completion_time1 = None
        self.completion_time2 = None
        self.start_time = None
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
        left_viz.addWidget(left_label)
        viz_layout.addLayout(left_viz)
        
        # Right visualization
        right_viz = QVBoxLayout()
        self.visualization2 = VisualizationWidget(self, is_left=False)
        right_viz.addWidget(self.visualization2)
        right_label = QLabel('Right Algorithm')
        right_label.setAlignment(Qt.AlignCenter)
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
        left_algo_name = self.left_algo_combo.currentText()
        right_algo_name = self.right_algo_combo.currentText()
        
        # Map algorithm names to functions
        algo_map = {
            'Merge Sort': lambda arr: self.merge_sort(arr),
            'Quick Sort': lambda arr: self.quick_sort(arr),
            'Bubble Sort': lambda arr: self.bubble_sort(arr),
            'Insertion Sort': lambda arr: self.insertion_sort(arr),
            'Selection Sort': lambda arr: self.selection_sort(arr),
            'Heap Sort': lambda arr: self.heap_sort(arr)
        }
        
        # Reset completion states
        self.arr1 = self.Barr.copy()
        self.arr2 = self.Barr.copy()
        self.complete1 = False
        self.complete2 = False
        self.completion_message = ""
        self.completion_time1 = None
        self.completion_time2 = None
        self.start_time = None
        
        # Start both algorithms
        self.current_algo1 = algo_map[left_algo_name](self.arr1)
        self.current_algo2 = algo_map[right_algo_name](self.arr2)
        self.timer.start(100 // self.settings.animation_speed)
    
    def update_visualization(self):
        if not self.start_time:
            self.start_time = QTimer.currentTime()
            
        if self.current_algo1 or self.current_algo2:
            try:
                if self.current_algo1:
                    next(self.current_algo1)
                if self.current_algo2:
                    next(self.current_algo2)
                self.visualization1.update()
                self.visualization2.update()
            except StopIteration:
                current_time = QTimer.currentTime()
                if self.current_algo1:
                    self.complete1 = True
                    self.current_algo1 = None
                    self.completion_time1 = current_time
                    if not self.complete2:
                        self.completion_message = "Left algorithm finished first!"
                if self.current_algo2:
                    self.complete2 = True
                    self.current_algo2 = None
                    self.completion_time2 = current_time
                    if not self.complete1:
                        self.completion_message = "Right algorithm finished first!"
                
                if not self.current_algo1 and not self.current_algo2:
                    self.timer.stop()
                    if self.complete1 and self.complete2:
                        # Compare completion times
                        time_diff = abs(self.completion_time1.msecsTo(self.completion_time2))
                        if time_diff < 100:  # If within 100ms, consider it simultaneous
                            self.completion_message = "Both algorithms finished simultaneously!"
                        elif self.completion_time1 < self.completion_time2:
                            self.completion_message = "Left algorithm finished first!"
                        else:
                            self.completion_message = "Right algorithm finished first!"
                
                self.visualization1.update()
                self.visualization2.update()
    
    def logout(self):
        self.main_window.show_login()
        
    # Sorting algorithms
    def bubble_sort(self, arr):
        for i in range(ARR_SIZE-1):
            for j in range(ARR_SIZE-1-i):
                if arr[j+1] < arr[j]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    yield
    
    def selection_sort(self, arr):
        for i in range(ARR_SIZE):
            min_idx = i
            for j in range(i+1, ARR_SIZE):
                if arr[j] < arr[min_idx]:
                    min_idx = j
                yield
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield
    
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

class VisualizationWidget(QWidget):
    def __init__(self, parent, is_left=True):
        super().__init__(parent)
        self.parent = parent
        self.is_left = is_left
        self.setMinimumHeight(WINDOW_HEIGHT - 150)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw array elements
        arr = self.parent.arr1 if self.is_left else self.parent.arr2
        complete = self.parent.complete1 if self.is_left else self.parent.complete2
        
        for i, val in enumerate(arr):
            color = self.parent.settings.default_color
            if complete:
                color = self.parent.settings.complete_color
            
            painter.fillRect(
                i * RECT_WIDTH,
                self.height() - val,
                RECT_WIDTH,
                val,
                color
            )
        
        # Draw completion message if both algorithms are done
        if self.parent.complete1 and self.parent.complete2 and self.parent.completion_message:
            painter.setPen(Qt.black)
            painter.setFont(QFont('Arial', 12))
            text_rect = self.rect()
            text_rect.setHeight(30)
            painter.drawText(text_rect, Qt.AlignCenter, self.parent.completion_message)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sorting Visualizer')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create stacked widget for switching between login and visualizer
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create and add windows
        self.login_window = LoginWindow(self)
        self.sorting_visualizer = SortingVisualizer(self)
        
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.sorting_visualizer)
        
        # Show login window first
        self.show_login()
        
    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_window)
        
    def show_sorting_visualizer(self):
        self.stacked_widget.setCurrentWidget(self.sorting_visualizer)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())