# Since I got 0 idea what project to make, let's modify a project that previously accepted
# Let's hope thats good
# It's time to recreate that plex-like movie tracker, except with TV shows specifically
# also.. even if Idea is not original that doesn't matter, good practice
# Made by sblnt
# Don't hate my formatting, I am a sys admin not a programmer


# First step, get API key from Movide db.
# scratch that, first step is recreating my github ssh key for WIndows.. shit



# search = tmdb.Search()
# response = search.tv(query='Avatar: The Last Airbender')

# top_result = response['results'][0]
# print(top_result['name'], top_result['first_air_date'])



import os
import requests
from io import BytesIO
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QPushButton, QLabel, QFileDialog
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import re
import tmdbsimple as tmdb

# Set your TMDb API key
tmdb.API_KEY = '993fd72d65a501e85e21e24beefe4330'   # Replace with your actual API key


class TVShowApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window Setup
        self.setWindowTitle("TV Show Organizer")
        self.resize(1000, 800)  # Increased size to accommodate grid
        self.center_window()

        # Central Widget and Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Grid Layout for displaying items
        self.grid_layout = QGridLayout()

        # Add a scroll area
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("background-color: #121212;")  # Match dark theme
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #121212;")  # Match dark theme
        scroll_content.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)

        # Buttons
        self.folder_button = QPushButton("Load Folder")
        self.settings_button = QPushButton("Settings")

        # Connect buttons to functions
        self.folder_button.clicked.connect(self.load_folder_function)
        self.settings_button.clicked.connect(self.open_settings_function)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.folder_button)
        button_layout.addWidget(self.settings_button)

        # Add components to main layout
        main_layout.addWidget(scroll_area)  # Add scrollable grid layout
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width, screen_height = screen.width(), screen.height()
        window_width = self.width()
        window_height = self.height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)

    def load_folder_function(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            contents = os.listdir(folder_path)
            self.clear_grid_layout(self.grid_layout)  # Clear existing items in the grid

            # Fetch the splash art once for the entire show
            show_name = self.extract_show_name(contents[0])
            image_pixmap = self.fetch_splash_art(show_name)
            
            for i, file_name in enumerate(contents):
                formatted_name = self.format_filename(file_name)
                custom_widget = CustomListItem(formatted_name, image_pixmap)
                self.grid_layout.addWidget(custom_widget, i // 2, i % 2)  # 2 items per row

    def open_settings_function(self):
        print("Settings button clicked!")

    def format_filename(self, file_name):
        """Format the file name by removing resolution and extra data."""
        base_name, _ = os.path.splitext(file_name)
        formatted_name = re.split(r'\b(1080p|720p|4K|2160p)\b', base_name, flags=re.IGNORECASE)[0]
        return formatted_name.replace(".", " ").strip()

    def extract_show_name(self, file_name):
        """Extract just the show name from a file name (e.g., 'Arrow' from 'Arrow.S01E01')."""
        base_name = self.format_filename(file_name)
        show_name = re.split(r'\bS\d{2}E\d{2}\b', base_name, maxsplit=1)[0].strip()
        return show_name

    def fetch_splash_art(self, show_name):
        """Fetch the splash art for the show from TMDb."""
        try:
            search = tmdb.Search()
            response = search.tv(query=show_name)
            if response['results']:
                poster_path = response['results'][0].get('poster_path')
                if poster_path:
                    image_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
                    response = requests.get(image_url, timeout=10)
                    pixmap = QPixmap()
                    pixmap.loadFromData(BytesIO(response.content).read())
                    return pixmap
        except Exception as e:
            print(f"Error fetching splash art: {e}")
        return QPixmap("path/to/placeholder_image.png")  # Replace with an actual placeholder image

    def clear_grid_layout(self, layout):
        """Clear all widgets from the grid layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class CustomListItem(QWidget):
    def __init__(self, title, image_pixmap=None):
        super().__init__()

        # Layout for the custom widget
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Image Label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 300)

        if image_pixmap:
            self.image_label.setPixmap(image_pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Title Label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        self.title_label.setWordWrap(True)  # Enable word wrapping
        self.title_label.setFixedWidth(200)  # Match the width of the image

        layout.addWidget(self.image_label)
        layout.addWidget(self.title_label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])

    # Apply dark mode stylesheet
    dark_mode_stylesheet = """
    QMainWindow {
        background-color: #121212;
        color: #ffffff;
    }

    QPushButton {
        background-color: #1f1f1f;
        color: #ffffff;
        border: 1px solid #333;
        padding: 5px;
        border-radius: 3px;
    }

    QPushButton:hover {
        background-color: #333333;
    }

    QScrollArea {
        background-color: #121212;
    }

    QLabel {
        color: #ffffff;
    }
    """
    app.setStyleSheet(dark_mode_stylesheet)

    window = TVShowApp()
    window.show()
    app.exec()