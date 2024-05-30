from PyQt5 import QtWidgets, QtGui
from MainUIClass.MainUIClasses import changeFilamentRoutine, controlScreen, displaySettings, ethernetSettingsPage, filamentSensor, firmwareUpdatePage, getFilesAndInfo, homePage, menuPage, networkInfoPage, networkSettingsPage, printLocationScreen, printRestore, printerStatus, settingsPage, settingsPage, socketConnections, softwareUpdatePage, start_keyboard, wifiSettingsPage, calibrationPage
import mainGUI
from MainUIClass.config import Development, _fromUtf8, setCalibrationPosition
import logging
from MainUIClass.threads import *
import styles
from MainUIClass.socket_qt import QtWebsocket

from MainUIClass.gui_elements import ClickableLineEdit

from MainUIClass.import_helper import load_classes      #used to import all classes at runtime

import dialog

class MainUIClass(QtWidgets.QMainWindow, mainGUI.Ui_MainWindow):
    
    def __init__(self, printer):
        '''
        This method gets called when an object of type MainUIClass is defined
        '''
        self.printer = printer
        setCalibrationPosition(self)

        super(MainUIClass, self).__init__()

        # classes = load_classes('mainUI_classes')
        # globals().update(classes)
        # Uncomment the above lines to import classes at runtime
        
        self.controlScreenInstance = controlScreen.controlScreen(self)
        self.printRestoreInstance = printRestore.printRestore(self)
        self.startKeyboard = start_keyboard.startKeyboard

        self.printerStatusInstance = printerStatus.printerStatus(self)    
        self.socketConnectionsInstance = socketConnections.socketConnections(self)
        #Initialising all pages/screens
        self.homePageInstance = homePage.homePage(self)
        self.menuPageInstance = menuPage.menuPage(self)
        self.calibrationPageInstance = calibrationPage.calibrationPage(self)
        self.getFilesAndInfoInstance = getFilesAndInfo.getFilesAndInfo(self)
        self.printLocationScreenInstance = printLocationScreen.printLocationScreen(self)
        self.changeFilamentRoutineInstance = changeFilamentRoutine.changeFilamentRoutine(self)
        self.networkInfoPageInstance = networkInfoPage.networkInfoPage(self)
        self.wifiSettingsPageInstance = wifiSettingsPage.wifiSettingsPage(self)
        self.ethernetSettingsPageInstance = ethernetSettingsPage.ethernetSettingsPage(self)
        self.displaySettingsInstance = displaySettings.displaySettings(self)
        self.softwareUpdatePageInstance = softwareUpdatePage.softwareUpdatePage(self)
        self.firmwareUpdatePageInstance = firmwareUpdatePage.firmwareUpdatePage(self)
        self.filamentSensorInstance = filamentSensor.filamentSensor(self)
        self.settingsPageInstance = settingsPage.settingsPage(self)
        self.networkSettingsPageInstance = networkSettingsPage.networkSettingsPage(self)
 
        if not Development:
            formatter = logging.Formatter("%(asctime)s %(message)s")
            self._logger = logging.getLogger("TouchUI")
            file_handler = logging.FileHandler("/home/pi/ui.log")
            file_handler.setFormatter(formatter)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self._logger.addHandler(file_handler)
            self._logger.addHandler(stream_handler)
        try:
            # if not Development:
                # self.__packager = asset_bundle.AssetBundle()
                # self.__packager.save_time()
                # self.__timelapse_enabled = self.__packager.read_match() if self.__packager.time_delta() else True
                # self.__timelapse_started = not self.__packager.time_delta()

                # self._logger.info("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                # print("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                # self._logger.info("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
                # print("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
            self.setupUi(self)
            self.stackedWidget.setCurrentWidget(self.loadingPage)
            self.controlScreenInstance.setStep(10)
            self.keyboardWindow = None
            self.changeFilamentHeatingFlag = False
            self.setHomeOffsetBool = False
            self.currentImage = None
            self.currentFile = None
            # if not Development:
            #     self.sanityCheck = ThreadSanityCheck(self._logger, virtual=not self.__timelapse_enabled)
            # else:
            self.sanityCheck = ThreadSanityCheck(virtual=False)
            self.sanityCheck.start()
            self.sanityCheck.loaded_signal.connect(self.proceed)
            self.sanityCheck.startup_error_signal.connect(self.handleStartupError)


            for spinbox in self.findChildren(QtWidgets.QSpinBox):
                lineEdit = spinbox.lineEdit()
                lineEdit.setReadOnly(True)
                lineEdit.setDisabled(True)
                p = lineEdit.palette()
                p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(40, 40, 40))
                lineEdit.setPalette(p)


        except Exception as e:
            self._logger.error(e)

    def setupUi(self, MainWindow):
        super(MainUIClass, self).setupUi(MainWindow)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gotham"))
        font.setPointSize(15)

        self.wifiPasswordLineEdit = ClickableLineEdit(self.wifiSettingsPage)
        self.wifiPasswordLineEdit.setGeometry(QtCore.QRect(0, 170, 480, 60))
        self.wifiPasswordLineEdit.setFont(font)
        self.wifiPasswordLineEdit.setStyleSheet(styles.textedit)
        self.wifiPasswordLineEdit.setObjectName(_fromUtf8("wifiPasswordLineEdit"))

        font.setPointSize(11)
        self.ethStaticIpLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.ethStaticIpLineEdit.setGeometry(QtCore.QRect(120, 10, 300, 30))
        self.ethStaticIpLineEdit.setFont(font)
        self.ethStaticIpLineEdit.setStyleSheet(styles.textedit)
        self.ethStaticIpLineEdit.setObjectName(_fromUtf8("ethStaticIpLineEdit"))

        self.ethStaticGatewayLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.ethStaticGatewayLineEdit.setGeometry(QtCore.QRect(120, 60, 300, 30))
        self.ethStaticGatewayLineEdit.setFont(font)
        self.ethStaticGatewayLineEdit.setStyleSheet(styles.textedit)
        self.ethStaticGatewayLineEdit.setObjectName(_fromUtf8("ethStaticGatewayLineEdit"))

        self.menuCartButton.setDisabled(True)

        if self.printer == "advanced":
            self.movie = QtGui.QMovie("templates/img/loading.gif")
        elif self.printer == "extended":
            self.movie = QtGui.QMovie("templates/img/loading-90.gif")
        self.loadingGif.setMovie(self.movie)
        self.movie.start()

    def safeProceed(self):
        '''
        When Octoprint server cannot connect for whatever reason, still show the home screen to conduct diagnostics
        '''
        self.movie.stop()
        if not Development:
            self.stackedWidget.setCurrentWidget(self.homePage)
            # self.Lock_showLock()
            self.setIPStatus()
        else:
            self.stackedWidget.setCurrentWidget(self.homePage)

        # # Text Input events
        self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
        self.ethStaticIpLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticIpLineEdit))
        self.ethStaticGatewayLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticGatewayLineEdit))

        # Button Events:

        # Home Screen:
        self.stopButton.setDisabled()
        # self.menuButton.pressed.connect(self.keyboardButton)
        self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.controlButton.setDisabled()
        self.playPauseButton.setDisabled()

        # MenuScreen
        self.menuBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        self.menuControlButton.setDisabled()
        self.menuPrintButton.setDisabled()
        self.menuCalibrateButton.setDisabled()
        self.menuSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))


        # Settings Page
        self.networkSettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.displaySettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
        self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
        self.OTAButton.setDisabled()
        self.versionButton.setDisabled()

        self.restartButton.pressed.connect(self.askAndReboot)
        self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
        self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

        # Network settings page
        self.networkInfoButton.pressed.connect(self.networkInfo)
        self.configureWifiButton.pressed.connect(self.wifiSettings)
        self.configureEthButton.pressed.connect(self.ethSettings)
        self.networkSettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Network Info Page
        self.networkInfoBackButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

        # WifiSetings page
        self.wifiSettingsSSIDKeyboardButton.pressed.connect(
            lambda: self.startKeyboard(self.wifiSettingsComboBox.addItem))
        self.wifiSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)

        # Ethernet setings page
        self.ethStaticCheckBox.stateChanged.connect(self.ethStaticChanged)
        # self.ethStaticCheckBox.stateChanged.connect(lambda: self.ethStaticSettings.setVisible(self.ethStaticCheckBox.isChecked()))
        self.ethStaticIpKeyboardButton.pressed.connect(lambda: self.ethShowKeyboard(self.ethStaticIpLineEdit))
        self.ethStaticGatewayKeyboardButton.pressed.connect(lambda: self.ethShowKeyboard(self.ethStaticGatewayLineEdit))
        self.ethSettingsDoneButton.pressed.connect(self.ethSaveStaticNetworkInfo)
        self.ethSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

        # Display settings
        self.rotateDisplay.pressed.connect(self.showRotateDisplaySettingsPage)
        self.calibrateTouch.pressed.connect(self.touchCalibration)
        self.displaySettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Rotate Display Settings
        self.rotateDisplaySettingsDoneButton.pressed.connect(self.saveRotateDisplaySettings)
        self.rotateDisplaySettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))

        # QR Code
        self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # SoftwareUpdatePage
        self.softwareUpdateBackButton.setDisabled()
        self.performUpdateButton.setDisabled()

        # Firmware update page
        self.firmwareUpdateBackButton.setDisabled()

        # Filament sensor toggle
        self.toggleFilamentSensorButton.setDisabled()

    def proceed(self):
        '''
        Startes websocket, as well as initialises button actions and callbacks. THis is done in such a manner so that the callbacks that dnepend on websockets
        load only after the socket is available which in turn is dependent on the server being available which is checked in the sanity check thread
        '''
        self.QtSocket = QtWebsocket()
        self.QtSocket.start()
        self.setActions()
        self.movie.stop()
        if not Development:
            self.stackedWidget.setCurrentWidget(self.homePage)
            # self.Lock_showLock()
            self.setIPStatus()
        else:
            self.stackedWidget.setCurrentWidget(self.homePage)

        self.filamentSensorInstance.isFilamentSensorInstalled()
        self.printRestoreInstance.onServerConnected()

    def setActions(self):

        '''
        defines all the Slots and Button events.
        '''

        self.socketConnectionsInstance.connect()  
        #Initialising all pages/screens
        self.homePageInstance.connect()  
        self.menuPageInstance.connect()  
        self.calibrationPageInstance.connect()  
        self.getFilesAndInfoInstance.connect()  
        self.printLocationScreenInstance.connect()  
        self.controlScreenInstance.connect()
        self.changeFilamentRoutineInstance.connect()
        self.networkInfoPageInstance.connect()
        self.wifiSettingsPageInstance.connect()
        self.ethernetSettingsPageInstance.connect()
        self.displaySettingsInstance.connect()
        self.softwareUpdatePageInstance.connect()
        self.firmwareUpdatePageInstance.connect()
        self.filamentSensorInstance.connect()
        self.settingsPageInstance.connect()
        self.networkSettingsPageInstance.connect()

        #  # Lock settings
        #     if not Development:
        #         self.lockSettingsInstance = lockSettings(self)
        
    def handleStartupError(self):
        if self.printer == "advanced":
            print('Shutting Down. Unable to connect')
            if dialog.WarningOk(self, "Error. Contact Support. Shutting down...", overlay=True):
                os.system('sudo shutdown now')
        
        elif self.printer == "extended":
            self.safeProceed()
            print('Unable to connect to Octoprint Server')
            if dialog.WarningOk(self, "Unable to connect to internal Server, try restoring factory settings", overlay=True):
                pass