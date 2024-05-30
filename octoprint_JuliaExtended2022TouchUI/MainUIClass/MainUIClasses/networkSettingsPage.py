class networkSettingsPage:
    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

    def connect(self):
        self.MainUIObj.networkInfoButton.pressed.connect(self.MainUIObj.wifiSettingsPageInstance.networkInfo)
        self.MainUIObj.configureWifiButton.pressed.connect(self.MainUIObj.wifiSettingsPageInstance.wifiSettings)
        self.MainUIObj.configureEthButton.pressed.connect(self.MainUIObj.ethernetSettingsPageInstance.ethSettings)
        self.MainUIObj.networkSettingsBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.settingsPage))
