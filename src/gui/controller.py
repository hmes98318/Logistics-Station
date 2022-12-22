import sys

# PyQt5 引擎 ---------------------------------------
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QFileDialog

# 用戶資料 -----------------------------------------
import UserData

# Socket 模塊-------------------------------------
sys.path.append("..")
from tcp.client import *
from tcp.server import *

# UI 介面 ----------------------------------------
from LoginWindow import Ui_LoginWindow
from MainWindow import Ui_MainWindow

client = Client()
server = Server()


# LoginWindow 登入畫面
class LoginWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setup_control()

        """ 窗體美化 """
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )
        """"""

    # TODO (要互動的元件擺放位置)
    def setup_control(self):

        # self.ui.pushButton.clicked.connect(self.buttonClicked)

        # LoginClose 關閉視窗
        self.ui.LoginClose.clicked.connect(self.LoginClose)
        # LoginMin 縮小視窗
        self.ui.LoginMin.clicked.connect(self.LoginMinimized)

        # LoginMove 滑鼠移動事件 (拖動視窗實現) -----------------------
        self.ui.LoginMove.mousePressEvent = self.loginPressEvent
        self.ui.LoginMove.mouseMoveEvent = self.loginMoveEvent
        self.ui.LoginMove.mouseReleaseEvent = self.loginReleaseEvent

        # Login 按鈕，檢查帳號資訊-----------------------------------
        self.ui.button_LogicIn.clicked.connect(self.loginIn)

    def LoginClose(self):
        print('關閉視窗!')
        self.close()

    def LoginMinimized(self):
        print('縮小視窗!')
        self.showMinimized()

    # 滑鼠移動事件(拖動視窗實現) -----------------------

    def loginPressEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def loginMoveEvent(self, e: QMouseEvent):
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def loginReleaseEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    # 登入檢查---------------------------------------

    def loginIn(self):
        input_ID = self.ui.input_ID.text()
        input_PW = self.ui.input_PW.text()

        # print(input_ID, type(input_ID))
        # print(input_PW, type(input_PW))

        if UserData.userData.get(input_ID, 'fail') != 'fail':
            if UserData.userData[input_ID] == input_PW:
                # from main import MainWindow
                MainWindow = MainWindow_controller()
                MainWindow.show()  # 開啟 MainWindow
                self.close()  # 關閉 LoginWindow
            else:
                pwfailResult = QMessageBox.warning(self,
                                                   '提示訊息', '密碼錯誤',
                                                   QMessageBox.Ok)
                return
        else:
            allfailResult = QMessageBox.warning(self,
                                                '提示訊息', '找不到此帳號! ',
                                                QMessageBox.Ok)
            return

        print("loginIn Clicked!")


# MainWindow 主要畫面
class MainWindow_controller(QtWidgets.QWidget):
    ProgressBarUpdate = pyqtSignal()  # 初始化自訂義信號槽

    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

        self.ui.stackedWidget.setCurrentIndex(2)  # 登入成功後初始介面為 Setting
        self.ui.button_Setting.setStyleSheet("background-color: rgb(255, 255, 255);;"
                                             "border-radius: 10px;")  # 更改顏色
        self.ui.button_Client.setEnabled(False)  # 未設定 IP 和 Port 時禁用
        self.ui.button_Server.setEnabled(False)  # 未設定 IP 和 Port 時禁用

        self.ui.input_ShowSavepath.setText('x')
        self.ui.input_serverIP.setText('0.0.0.0')
        self.ui.button_Startlistening.setEnabled(False)  # 開始聆聽 button 禁用 (沒有檔案)
        self.ui.button_SelectfFile.setEnabled(True)  # 選擇檔案 button 啟用
        self.ui.button_Stoplistening.setEnabled(False)  # 終止聆聽 button 禁用

        # --------------測試區域----------------------------------------
        self.sFileLayoutVisible(False)
        self.ui.Layout_SelectFile.setAlignment(Qt.AlignTop)  # 置上對齊
        self.ui.button_Startlistening.setEnabled(False)

        self.cFileLayoutVisible(False)
        self.ui.Layout_cRequireFile.setAlignment(Qt.AlignTop)  # 置上對齊
        # ------------------------------------------------------------

        self.thread_ServerListening = QThread()  # 定義 Server 新執行序
        self.thread_ClientReceiveFile = QThread()  # 定義 Client 新執行序
        self.ProgressBarUpdate.connect(self.UpdateProgressBar_ReceiveFile)  # 連接自訂義信號槽函數

        """ 窗體美化 """
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )

        """"""

    # TODO (要互動的元件擺放位置)
    def setup_control(self):
        # self.ui.pushButton.clicked.connect(self.buttonClicked)

        # MainClose 關閉視窗
        self.ui.MainClose.clicked.connect(self.MainClose)
        # MainMin 縮小視窗
        self.ui.MainMin.clicked.connect(self.MainMinimized)

        # MainMove 滑鼠移動事件 (拖動視窗實現) -----------------------
        self.ui.MainMove.mousePressEvent = self.MainPressEvent
        self.ui.MainMove.mouseMoveEvent = self.MainMoveEvent
        self.ui.MainMove.mouseReleaseEvent = self.MainReleaseEvent

        # MainWindow 按鈕事件 (單窗口多視窗切換實現) ------------------------
        self.ui.button_Client.clicked.connect(self.SwitchToClientPage)
        self.ui.button_Server.clicked.connect(self.SwitchToServerPage)
        self.ui.button_Setting.clicked.connect(self.SwitchToSettingPage)
        self.ui.button_User.clicked.connect(self.SwitchToUserPage)

        # Client 頁面按鈕事件 -----------------------------------------
        self.ui.button_RequireFile.clicked.connect(self.ClientRequireFile)

        # Server 頁面按鈕事件 -----------------------------------------
        self.ui.button_Startlistening.clicked.connect(self.StartListening)
        self.ui.button_Stoplistening.clicked.connect(self.StopListening)
        self.ui.button_SelectfFile.clicked.connect(self.SelectSendFile)

        # Setting 頁面按鈕事件 -----------------------------------------
        self.ui.button_OpenSaveFolder.clicked.connect(self.OpenSaveFolder)
        self.ui.button_SettingSave.clicked.connect(self.SettingSave)

    # 各事件對應函數 ------------------------------------------------------------------------------------------------------

    def MainClose(self):
        print('關閉視窗!')
        self.close()

    def MainMinimized(self):
        print('縮小視窗!')
        self.showMinimized()

    # Client -----------------------------------------------------------------------------------------------------------

    def SwitchToClientPage(self):
        self.ui.stackedWidget.setCurrentIndex(0)  # 切換 Stack Widget 到 (索引值 0 / Client) 頁
        # self.ui.label_schedule.setText(str(0))
        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

    def ClientRequireFile(self):
        # self.ui.label_schedule.setText(str(0))
        self.ui.progressBar_RecevieFile.setMaximum(100)  # 進度條最大值 100
        self.ui.button_RequireFile.setEnabled(False)
        self.ui.button_RequireFile.setText('正在下載')
        self.thread_ClientReceiveFile.run = self.QThread_ClientReceiving
        self.thread_ClientReceiveFile.start()

    def QThread_ClientReceiving(self):
        self.ui.button_RequireFile.setEnabled(False)
        self.ui.button_RequireFile.setText('正在連接 Server...')

        SUCCESS_START = client.start()
        if SUCCESS_START == False :
            print('### Client connect fail')
            self.ui.button_RequireFile.setEnabled(True)
            self.ui.button_RequireFile.setText('連接 Server 失敗，確認目標 IP 位置無誤後重試')
            self.thread_ClientReceiveFile.quit() # 掛起線程
            return

        SUCCESS_ASKHEADER = client.askHeader()
        if SUCCESS_ASKHEADER == False : 
            print('### Client askHeader() fail')
            self.ui.button_RequireFile.setEnabled(True)
            self.ui.button_RequireFile.setText('連接 Server 失敗，確認目標 IP 位置無誤後重試')
            self.thread_ClientReceiveFile.quit() # 掛起線程
            return


        print(f'connection: {client.showConnection()}')

        self.cFileLayoutVisible(True)
        print('### start askFile()')
        self.ui.button_RequireFile.setText('下載中...')
        client.askFile(self.ProgressBarUpdate)


        self.ui.button_RequireFile.setEnabled(True)
        self.ui.button_RequireFile.setText('連線至 Server 獲取檔案')
        self.thread_ClientReceiveFile.quit() # 掛起線程
        return

    def UpdateProgressBar_ReceiveFile(self):
        self.ui.progressBar_RecevieFile.setValue(int(client.showProgress()))  # 增加進度條

    # Server -----------------------------------------------------------------------------------------------------------

    def SwitchToServerPage(self):
        self.ui.stackedWidget.setCurrentIndex(1)  # 切換 Stack Widget 到 (索引值 1 / Server) 頁

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Server,
                                  self.ui.button_Client,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

        if server.showUser() == {} and False:
            self.sFileLayoutVisible(False)
            self.ui.Layout_SelectFile.setAlignment(Qt.AlignTop)
            self.ui.button_Startlistening.setEnabled(False)

        # print(server.host + ' ' + str(server.port))

    def SelectSendFile(self):
        # 開啟資料夾，回傳型態為 tuple
        folder_path = QFileDialog.getOpenFileName(self,
                                                  "Open file",
                                                  "./")  # start path
        print(folder_path)
        file_name = os.path.basename(folder_path[0])
        file_size = os.path.getsize(folder_path[0]) / 1024  # 1024 byte = 1 kb
        print(file_name)
        print(file_size)
        server.setFile(folder_path[0])
        try:
            self.ui.label_Filename.setText(file_name)
            if file_size < 1024:
                self.ui.label_Filesize.setText(str('%.2f' % file_size) + " KB")
            elif file_size < 1024 * 1024:
                self.ui.label_Filesize.setText(str('%.2f' % (file_size / 1024)) + " MB")
            elif file_size < 1024 * 1024 * 1024:
                self.ui.label_Filesize.setText(str('%.2f' % (file_size / 1024 / 1024)) + " GB")
            else:
                self.ui.label_Filesize.setText(str('%.2f' % (file_size / 1024 / 1024 / 1024)) + " TB")
            self.ui.button_Startlistening.setEnabled(True)
            self.sFileLayoutVisible(True)
            return
        except Exception:
            print("沒有選檔案@w@,或是檔案類型錯誤")

    def StartListening(self):
        self.ui.button_Startlistening.setEnabled(False)  # 開始聆聽 button 禁用
        self.ui.button_SelectfFile.setEnabled(False)  # 聆聽時選擇檔案 button 禁用
        self.ui.button_Stoplistening.setEnabled(True)  # 終止聆聽 button 啟用

        self.thread_ServerListening.run = self.QThread_ServerListening
        self.thread_ServerListening.start()

    def QThread_ServerListening(self):
        server.init()
        server.startListening()

    def StopListening(self):
        if server.showUser() == {}:
            self.ui.button_Startlistening.setEnabled(True)  # 開始聆聽 button 啟用
            self.ui.button_SelectfFile.setEnabled(True)  # 結束聆聽後選擇檔案 button 啟用
            self.ui.button_Stoplistening.setEnabled(False)  # 終止聆聽 button 禁用

            self.sFileLayoutVisible(False)
            self.ui.Layout_SelectFile.setAlignment(Qt.AlignTop)
            self.ui.button_Startlistening.setEnabled(False)

            server.stop()
            self.thread_ServerListening.quit()
        else:
            result = QMessageBox.warning(self,
                                         '---------⊗警告訊息⊗---------',
                                         '當前 client 端正在連接!!!\n',
                                         QMessageBox.Ok)
            if result == QMessageBox.Ok:
                return

    # Setting ----------------------------------------------------------------------------------------------------------

    def SwitchToSettingPage(self):
        self.ui.stackedWidget.setCurrentIndex(2)  # 切換 Stack Widget 到 (索引值 2 / Setting) 頁

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Setting,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_User)

    def SettingSave(self):
        while 1:
            try:
                input_clientIP = self.ui.input_clientIP.text()
                input_clientPort = int(self.ui.input_clientPort.text())
                input_serverIP = self.ui.input_serverIP.text()
                input_serverPort = int(self.ui.input_serverPort.text())

                if self.ui.input_ShowSavepath.text() == 'x':
                    QMessageBox.warning(self,
                                        '---------警告訊息---------',
                                        '請選擇保存路徑!\n',
                                        QMessageBox.Ok)
                    return

                client.setHost(input_clientIP, input_clientPort)
                server.setHost(input_serverIP, input_serverPort)

                QMessageBox.information(self,
                                        '提示訊息', '保存成功',
                                        QMessageBox.Ok)
                self.ui.button_Client.setEnabled(True)
                self.ui.button_Server.setEnabled(True)
                return
            except TypeError and ValueError:
                result = QMessageBox.warning(self,
                                             '---------警告訊息---------',
                                             '請確認輸入正確的數值!\n'
                                             'IPv4 範例 197.128.0.1\n'
                                             'Port 範例 1234',
                                             QMessageBox.Ok)
                if result == QMessageBox.Ok:
                    print('TypeError or ValueError')
                    return

    def OpenSaveFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self,
                                                       "Open folder",
                                                       "./")  # start path

        client.setFolder(folder_path)  # 設置 client 儲存路徑
        # print(folder_path)
        self.ui.input_ShowSavepath.setText(folder_path)

    # User -------------------------------------------------------------------------------------------------------------

    def SwitchToUserPage(self):
        self.ui.stackedWidget.setCurrentIndex(3)  # 切換 Stack Widget 到 (索引值 3 / User) 頁

        # 顏色轉換
        # button_union = [self.ui.button_User, self.ui.button_Client, self.ui.button_Server, self.ui.button_Setting]
        self.button_setStyleSheet(self.ui.button_User,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting)

    # 滑鼠移動事件(拖動視窗實現) --------------------------------------------------------------------------------------------

    def MainPressEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def MainMoveEvent(self, e: QMouseEvent):
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def MainReleaseEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    # 奇怪的東西 ---------------------------------------------------------------------------------------------------------

    def sFileLayoutVisible(self, flag):
        self.ui.label_Filesize.setVisible(flag)
        self.ui.label_Filename.setVisible(flag)
        self.ui.hint_Filesize.setVisible(flag)
        self.ui.hint_Filename.setVisible(flag)

        self.ui.Layout_FileInfo.setEnabled(flag)
        # self.ui.Layout_Filesize.setEnabled(flag)
        # self.ui.Layout_Filename.setEnabled(flag)

    def cFileLayoutVisible(self, flag):
        # self.ui.label_cFilesize.setVisible(flag)
        # self.ui.label_cFilename.setVisible(flag)
        self.ui.label_spacer1.setVisible(flag)
        self.ui.label_spacer2.setVisible(flag)
        self.ui.hint_cFileize.setVisible(flag)
        self.ui.hint_cFilename.setVisible(flag)
        self.ui.hint_schedule.setVisible(flag)
        self.ui.progressBar_RecevieFile.setVisible(flag)

        self.ui.Layout_cFileInfo.setEnabled(flag)

    def button_setStyleSheet(self, NowFocus: QtWidgets.QPushButton,
                             Other1: QtWidgets.QPushButton,
                             Other2: QtWidgets.QPushButton,
                             Other3: QtWidgets.QPushButton):

        otherPage_StyleSheet = "background-color: rgba(36, 67, 124, 50);" \
                               "border-radius: 10px;" \
                               "color: rgb(255, 255, 255);"
        nowPage_StyleSheet = "background-color: rgba(255, 255, 255, 255);" \
                             "border-radius: 10px;"

        NowFocus.setStyleSheet(nowPage_StyleSheet)
        Other1.setStyleSheet(otherPage_StyleSheet)
        Other2.setStyleSheet(otherPage_StyleSheet)
        Other3.setStyleSheet(otherPage_StyleSheet)


if __name__ == '__main__':
    

    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = LoginWindow_controller()
    LoginWindow.show()
    sys.exit(app.exec_())
