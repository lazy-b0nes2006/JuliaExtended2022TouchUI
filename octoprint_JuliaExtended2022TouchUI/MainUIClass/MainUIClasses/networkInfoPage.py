class networkInfoPage:
    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

    def connect(self):
        self.MainUIObj.networkInfoBackButton.pressed.connect(
            lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.networkSettingsPage))
