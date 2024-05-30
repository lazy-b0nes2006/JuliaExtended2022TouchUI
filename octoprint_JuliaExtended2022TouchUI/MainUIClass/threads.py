from PyQt5 import QtCore
from octoprintAPI import octoprintAPI
import subprocess
from MainUIClass.config import ip, apiKey, Development
import time
import os
from MainUIClass.network_utils import getIP

octopiclient = octoprintAPI(ip, apiKey)

class ThreadSanityCheck(QtCore.QThread):

    loaded_signal = QtCore.pyqtSignal()
    startup_error_signal = QtCore.pyqtSignal()

    def __init__(self, logger = None, virtual=False):
        super(ThreadSanityCheck, self).__init__()
        self.MKSPort = None
        self.virtual = virtual
        if not Development:
            self._logger = logger

    def run(self):
        global octopiclient
        self.shutdown_flag = False
        # get the first value of t1 (runtime check)
        uptime = 0
        # keep trying untill octoprint connects
        while (True):
            # Start an object instance of octopiAPI
            try:
                if (uptime > 30):
                    self.shutdown_flag = True
                    self.startup_error_signal.emit()
                    break
                #octopiclient = octoprintAPI(ip, apiKey)
                if not self.virtual:
                    result = subprocess.Popen("dmesg | grep 'ttyUSB'", stdout=subprocess.PIPE, shell=True).communicate()[0]
                    result = result.split(b'\n')  # each ssid and pass from an item in a list ([ssid pass,ssid paas])
                    print(result)
                    result = [s.strip() for s in result]
                    for line in result:
                        if b'FTDI' in line:
                            self.MKSPort = line[line.index(b'ttyUSB'):line.index(b'ttyUSB') + 7].decode('utf-8')
                            print(self.MKSPort)
                        if b'ch34' in line:
                            self.MKSPort = line[line.index(b'ttyUSB'):line.index(b'ttyUSB') + 7].decode('utf-8')
                            print(self.MKSPort)

                    if not self.MKSPort:
                        octopiclient.connectPrinter(port="VIRTUAL", baudrate=115200)
                    else:
                        octopiclient.connectPrinter(port="/dev/" + self.MKSPort, baudrate=115200)
                break
            except Exception as e:
                time.sleep(1)
                uptime = uptime + 1
                print("Not Connected!")
        if not self.shutdown_flag:
            self.loaded_signal.emit()

class ThreadFileUpload(QtCore.QThread):
    def __init__(self, file, prnt=False):
        super(ThreadFileUpload, self).__init__()
        self.file = file
        self.prnt = prnt

    def run(self):

        try:
            exists = os.path.exists(self.file.replace(".gcode", ".png"))
        except:
            exists = False
        if exists:
            octopiclient.uploadImage(self.file.replace(".gcode", ".png"))

        if self.prnt:
            octopiclient.uploadGcode(file=self.file, select=True, prnt=True)
        else:
            octopiclient.uploadGcode(file=self.file, select=False, prnt=False)

class ThreadRestartNetworking(QtCore.QThread):
    WLAN = "wlan0"
    ETH = "eth0"
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, interface):
        super(ThreadRestartNetworking, self).__init__()
        self.interface = interface
    def run(self):
        self.restart_interface()
        attempt = 0
        while attempt < 3:
            # print(getIP(self.interface))
            if getIP(self.interface):
                self.signal.emit(getIP(self.interface))
                break
            else:
                attempt += 1
                time.sleep(5)
        if attempt >= 3:
            self.signal.emit(None)

    def restart_interface(self):
        '''
        restars wlan0 wireless interface to use new changes in wpa_supplicant.conf file
        :return:
        '''
        if self.interface == "wlan0":
            subprocess.call(["wpa_cli","-i",  self.interface, "reconfigure"], shell=False)
        if self.interface == "eth0":
            subprocess.call(["ifconfig",  self.interface, "down"], shell=False)
            time.sleep(1)
            subprocess.call(["ifconfig", self.interface, "up"], shell=False)
        # subprocess.call(["ifdown", "--force", self.interface], shell=False)
        # subprocess.call(["ifup", "--force", self.interface], shell=False)
        time.sleep(5)
