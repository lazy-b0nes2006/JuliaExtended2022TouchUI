class socketConnections:
    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

    def connect(self):
        self.MainUIObj.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)
        self.MainUIObj.QtSocket.temperatures_signal.connect(self.updateTemperature)
        self.MainUIObj.QtSocket.status_signal.connect(self.updateStatus)
        self.MainUIObj.QtSocket.print_status_signal.connect(self.updatePrintStatus)
        self.MainUIObj.QtSocket.update_started_signal.connect(self.softwareUpdateProgress)
        self.MainUIObj.QtSocket.update_log_signal.connect(self.softwareUpdateProgressLog)
        self.MainUIObj.QtSocket.update_log_result_signal.connect(self.softwareUpdateResult)
        self.MainUIObj.QtSocket.update_failed_signal.connect(self.updateFailed)
        self.MainUIObj.QtSocket.connected_signal.connect(self.onServerConnected)
        self.MainUIObj.QtSocket.filament_sensor_triggered_signal.connect(self.filamentSensorHandler)
        self.MainUIObj.QtSocket.firmware_updater_signal.connect(self.firmwareUpdateHandler)

    def getZHomeOffset(self, offset):
        self.MainUIObj.calibrationPageInstance.getZHomeOffset(offset)

    def updateTemperature(self, temperature):
        self.MainUIObj.printerStatusInstance.updateTemperature(temperature)
        
    def updatePrintStatus(self, file):
        self.MainUIObj.printerStatusInstance.updatePrintStatus(file)
        
    def updateStatus(self, status):
        self.MainUIObj.printerStatusInstance.updateStatus(status)

    def softwareUpdateResult(self, data):
        self.MainUIObj.softwareUpdatesInstance.softwareUpdateResult(data)

    def softwareUpdateProgress(self, data):
        self.MainUIObj.softwareUpdatesInstance.softwareUpdateProgress(data)

    def softwareUpdateProgressLog(self, data):
        self.MainUIObj.softwareUpdatesInstance.softwareUpdateProgressLog(data)

    def updateFailed(self, data):
        self.MainUIObj.softwareUpdatesInstance.UpdateFailed(data)

    def onServerConnected(self):
        self.MainUIObj.printRestoreInstance.onServerConnected()

    def firmwareUpdateHandler(self, data):
        self.MainUIObj.firmwareUpdatePageInstance.firmwareUpdateHandler(data)

    def filamentSensorHandler(self, data):
        self.MainUIObj.filamentSensorInstance.filamentSensorHandler(data)
        
