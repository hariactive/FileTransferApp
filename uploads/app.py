import sys
import os
import threading
from flask import Flask, request, send_from_directory, render_template_string
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import requests
import time

# Flask Server Code
flask_app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@flask_app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string('''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <h2>Uploaded Files</h2>
    <ul>
    {% for file in files %}
      <li><a href="{{ url_for('uploaded_file', filename=file) }}">{{ file }}</a></li>
    {% endfor %}
    </ul>
    ''', files=files)

@flask_app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return 'File uploaded successfully'
    return 'No file uploaded'

@flask_app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Thread to run Flask server
def run_flask():
    flask_app.run(host='0.0.0.0', port=5000)

# PyQt5 GUI Code
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Hari Og- File Transfer'
        self.setWindowIcon(QIcon('lojo.png'))
        self.initUI()

        # Start the Flask server in a separate thread
        self.server_thread = threading.Thread(target=run_flask)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Wait a bit to ensure the server starts
        time.sleep(1)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.upload_button = QPushButton('Upload File', self)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        self.label = QLabel('Upload files via http://<your_ip>:5000\n For Ex. http://192.168.88.99:5000 in your browser', self)
        # self.label = QLabel('Upload files via http://192.168.88.99:5000', self)
        self.label.setStyleSheet("font-size: 14px; margin: 20px;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.show()

    def upload_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File to Upload", "", "All Files (*);;Python Files (*.py)", options=options)
        if file_name:
            self.upload_to_server(file_name)

    def upload_to_server(self, file_path):
        url = 'http://localhost:5000'
        files = {'file': open(file_path, 'rb')}
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                self.label.setText(f'Uploaded: {os.path.basename(file_path)}')
            else:
                self.label.setText('Upload failed')
        except requests.exceptions.RequestException as e:
            self.label.setText(f'Upload failed: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply a custom style to the application
    app.setStyleSheet("""
        QWidget {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
    """)

    ex = App()
    sys.exit(app.exec_())
