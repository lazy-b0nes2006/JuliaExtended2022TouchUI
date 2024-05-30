import sys
from MainUIClass.MainUIClass_def import MainUIClass
from PyQt5 import QtWidgets

#if not Development:
    #import RPi.GPIO as GPIO
    #GPIO.setmode(GPIO.BCM)  # Use the board numbering scheme
    #GPIO.setwarnings(False)  # Disable GPIO warnings H

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Intialize the library (must be called once before other functions).
    # Creates an object of type MainUiClass
    MainWindow = MainUIClass("extended")
    MainWindow.show()
    # MainWindow.showFullScreen()
    # MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    # Create NeoPixel object with appropriate configuration.
    # charm = FlickCharm()
    # charm.activateOn(MainWindow.FileListWidget)
sys.exit(app.exec_())
