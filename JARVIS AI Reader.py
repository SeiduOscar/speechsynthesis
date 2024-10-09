import sys
import pyttsx3
import pyperclip
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog,
    QComboBox, QTabWidget, QGridLayout, QLabel, QSlider, QCheckBox, QColorDialog,
    QHBoxLayout, QLineEdit, QToolTip, QMessageBox, QPlainTextEdit
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt, QTimer

class JarvisAIRedReader(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.is_reading = False
        self.current_text = ""
        self.current_pos = 0
        self.chunk_size = 500  # Number of characters per chunk
        self.timer = QTimer()
        self.timer.timeout.connect(self.readNextChunk)
        self.history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JARVIS AI Reader")
        self.setGeometry(300, 300, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabWidget = QTabWidget()
        self.layout.addWidget(self.tabWidget)

        self.textTab = QWidget()
        self.tabWidget.addTab(self.textTab, "Text")

        self.fileTab = QWidget()
        self.tabWidget.addTab(self.fileTab, "File")

        self.settingsTab = QWidget()
        self.tabWidget.addTab(self.settingsTab, "Settings")

        self.createTextTab()
        self.createFileTab()
        self.createSettingsTab()

        # Load previously saved settings if available
        self.loadSettings()

    def createTextTab(self):
        layout = QVBoxLayout()
        self.textTab.setLayout(layout)

        self.textEdit = QTextEdit()
        layout.addWidget(self.textEdit)

        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)

        self.readButton = QPushButton("Play")
        self.readButton.clicked.connect(self.readOut)
        buttonLayout.addWidget(self.readButton)

        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.stopReading)
        self.stopButton.setEnabled(False)
        buttonLayout.addWidget(self.stopButton)

        self.clipboardButton = QPushButton("Get from Clipboard")
        self.clipboardButton.clicked.connect(self.getFromClipboard)
        buttonLayout.addWidget(self.clipboardButton)

        self.historyButton = QPushButton("Show History")
        self.historyButton.clicked.connect(self.showHistory)
        buttonLayout.addWidget(self.historyButton)

    def createFileTab(self):
        layout = QVBoxLayout()
        self.fileTab.setLayout(layout)

        self.fileFormatComboBox = QComboBox()
        self.fileFormatComboBox.addItem("PDF")
        self.fileFormatComboBox.addItem("DOCX")
        self.fileFormatComboBox.addItem("TXT")
        self.fileFormatComboBox.addItem("PPT")
        layout.addWidget(self.fileFormatComboBox)

        self.openFileButton = QPushButton("Open File")
        self.openFileButton.clicked.connect(self.openFile)
        layout.addWidget(self.openFileButton)

        self.filePathLabel = QLabel("No file selected")
        layout.addWidget(self.filePathLabel)

    def createSettingsTab(self):
        layout = QGridLayout()
        self.settingsTab.setLayout(layout)

        self.voiceLabel = QLabel("Voice:")
        layout.addWidget(self.voiceLabel, 0, 0)

        self.voiceComboBox = QComboBox()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            self.voiceComboBox.addItem(voice.name)
        self.voiceComboBox.currentIndexChanged.connect(self.changeVoice)
        layout.addWidget(self.voiceComboBox, 0, 1)

        self.rateLabel = QLabel("Rate:")
        layout.addWidget(self.rateLabel, 1, 0)

        self.rateSlider = QSlider(Qt.Horizontal)
        self.rateSlider.setMinimum(50)
        self.rateSlider.setMaximum(200)
        self.rateSlider.setValue(self.engine.getProperty('rate'))
        self.rateSlider.valueChanged.connect(self.changeRate)
        layout.addWidget(self.rateSlider, 1, 1)

        self.volumeLabel = QLabel("Volume:")
        layout.addWidget(self.volumeLabel, 2, 0)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(int(self.engine.getProperty('volume') * 100))
        self.volumeSlider.valueChanged.connect(self.changeVolume)
        layout.addWidget(self.volumeSlider, 2, 1)

        self.colorLabel = QLabel("Color:")
        layout.addWidget(self.colorLabel, 3, 0)

        self.colorButton = QPushButton("Change Color")
        self.colorButton.clicked.connect(self.changeColor)
        layout.addWidget(self.colorButton, 3, 1)

        self.darkModeCheckBox = QCheckBox("Dark Mode")
        self.darkModeCheckBox.stateChanged.connect(self.toggleDarkMode)
        layout.addWidget(self.darkModeCheckBox, 4, 0, 1, 2)

        self.pauseDurationLabel = QLabel("Pause Duration (ms):")
        layout.addWidget(self.pauseDurationLabel, 5, 0)

        self.pauseDurationInput = QLineEdit()
        self.pauseDurationInput.setText("1000")  # Default value
        layout.addWidget(self.pauseDurationInput, 5, 1)

        self.saveSettingsButton = QPushButton("Save Settings")
        self.saveSettingsButton.clicked.connect(self.saveSettings)
        layout.addWidget(self.saveSettingsButton, 6, 0, 1, 2)

    def readOut(self):
        if self.is_reading:
            return
        self.is_reading = True
        self.current_text = self.textEdit.toPlainText()
        self.current_pos = 0
        self.timer.start(100)  # Start the timer to read text in chunks
        self.stopButton.setEnabled(True)
        self.readButton.setEnabled(False)
        self.history.append(self.current_text)

    def readNextChunk(self):
        if self.current_pos >= len(self.current_text):
            self.stopReading()
            return
        chunk = self.current_text[self.current_pos:self.current_pos + self.chunk_size]
        self.engine.say(chunk)
        self.engine.runAndWait()  # Important for pyttsx3 to process the speech
        self.current_pos += self.chunk_size

    def stopReading(self):
        self.engine.stop()
        self.is_reading = False
        self.timer.stop()
        self.stopButton.setEnabled(False)
        self.readButton.setEnabled(True)

    def getFromClipboard(self):
        text = pyperclip.paste()
        self.textEdit.setText(text)

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.filePathLabel.setText(file_path)
            with open(file_path, 'r') as file:
                text = file.read()
                self.textEdit.setText(text)

    def changeVoice(self):
        selected_voice = self.voiceComboBox.currentText()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice.name == selected_voice:
                self.engine.setProperty('voice', voice.id)
                break

    def changeRate(self):
        self.engine.setProperty('rate', self.rateSlider.value())

    def changeVolume(self):
        self.engine.setProperty('volume', self.volumeSlider.value() / 100)

    def changeColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()}")

    def toggleDarkMode(self, state):
        if state == Qt.Checked:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            self.setPalette(palette)
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            self.setPalette(palette)

    def saveSettings(self):
        settings = {
            'voice': self.voiceComboBox.currentText(),
            'rate': self.rateSlider.value(),
            'volume': self.volumeSlider.value() / 100,
            'pause_duration': int(self.pauseDurationInput.text())
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            self.showMessage("Settings Saved", "Your settings have been saved successfully.")
        except Exception as e:
            self.showMessage("Error", f"An error occurred while saving settings: {e}")

    def loadSettings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.voiceComboBox.setCurrentText(settings.get('voice', ''))
            self.rateSlider.setValue(settings.get('rate', 150))
            self.volumeSlider.setValue(int(settings.get('volume', 0.5) * 100))
            self.pauseDurationInput.setText(str(settings.get('pause_duration', 1000)))
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            self.showMessage("Error", "Failed to load settings. Settings file might be corrupted.")

    def showHistory(self):
        history_text = "\n\n".join(self.history)
        history_dialog = QWidget()
        layout = QVBoxLayout()
        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(history_text)
        layout.addWidget(text_edit)
        history_dialog.setLayout(layout)
        history_dialog.setWindowTitle("History")
        history_dialog.setGeometry(400, 300, 400, 300)
        history_dialog.show()

    def showMessage(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    reader = JarvisAIRedReader()
    reader.show()
    sys.exit(app.exec_())
