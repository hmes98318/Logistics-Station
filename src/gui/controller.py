# -*- coding: utf-8 -*-
import os
import sys

sys.path.append('./src')  # 更改模塊導入路徑

# PyQt5 引擎 ---------------------------------------
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QFileDialog

# 用戶資料 -----------------------------------------
from data.UserData import *

# Socket 模塊-------------------------------------
from tcp.Client import *
# from server.src.Server import *

# UI 介面 ----------------------------------------
from gui.LoginWindow import Ui_LoginWindow
from gui.MainWindow import Ui_MainWindow

client = Client()
# server = Server()

GUI = 'GUI:'
DEFAULT_SAVE_DIR = f'{os.path.dirname(__file__)}/save'.replace('\\','/') # .\foo\bar -> ./foo/bar



# LoginWindow 登入畫面
class LoginWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setup_control()

        # --- 窗體美化 ---#
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )
        # ---------------#

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
        print(GUI, '關閉視窗!')
        self.close()

    def LoginMinimized(self):
        print(GUI, '縮小視窗!')
        self.showMinimized()

    ###---------- 滑鼠移動事件(拖動視窗實現) ----------###

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

    ###----------------------------------------------###

    ###----------------- 登入檢查 -----------------###

    def loginIn(self):
        input_ID = self.ui.input_ID.text()
        input_PW = self.ui.input_PW.text()

        # print(GUI, input_ID, type(input_ID))
        # print(GUI, input_PW, type(input_PW))

        if userData.get(input_ID, 'fail') != 'fail':
            if userData[input_ID] == input_PW:
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
                                                '提示訊息', '找不到此帳號!',
                                                QMessageBox.Ok)
            return
        print(GUI, 'LoginIn clicked!')

    ###-------------------------------------------###


# MainWindow 主要畫面
class MainWindow_controller(QtWidgets.QWidget):
    DownloadProgressBarUpdate = pyqtSignal()  # 初始化自訂義信號槽
    UploadProgressBarUpdate = pyqtSignal()
    recvKeyList = []

    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

        self.ui.stackedWidget.setCurrentIndex(0)  # 登入成功後初始介面為 Setting
        self.ui.input_clientIP.setText('proxy.ggwp.tw')
        self.ui.input_clientPort.setText('7000')
        self.SettingSave()

        self.ui.button_Client.setStyleSheet('background-color: rgb(255, 255, 255);;'
                                             'border-radius: 10px;')  # 更改顏色

        #self.ui.button_Client.setEnabled(False)  # 未設定 IP 和 Port 時禁用
        #self.ui.button_Server.setEnabled(False)  # 未設定 IP 和 Port 時禁用

        self.ui.input_ShowSavepath.setText(DEFAULT_SAVE_DIR) # 預設路徑
        self.ui.button_Startlistening.setEnabled(False)  # 開始聆聽 button 禁用 (沒有檔案)
        self.ui.button_SelectfFile.setEnabled(True)  # 選擇檔案 button 啟用

        self.sFileLayoutVisible(False)
        self.ui.Layout_SelectFile.setAlignment(Qt.AlignTop)  # 置上對齊
        self.ui.button_Startlistening.setEnabled(False)
        self.cFileLayoutVisible(False)
        self.cFileDownloadVisible(False)
        self.ui.Layout_cRequireFile.setAlignment(Qt.AlignTop)  # 置上對齊

        # --------------測試區域----------------------------------------
        self.ui.progressBar_RecevieFile.setValue(0)  # 進度條 0 
        self.ui.progressBar_SendFile.setValue(0)
        # ------------------------------------------------------------

        # ------------定義執行序------------
        self.thread_SendFile = QThread() # 發送包裹
        self.thread_ClientReceiveHeader = QThread()  # 接收包裹 header
        self.thread_ClientReceiveFile = QThread()  # 接收包裹 
        self.UploadProgressBarUpdate.connect(self.UpdataprogressBar_SendFile)  # 連接自訂義信號槽函數
        self.DownloadProgressBarUpdate.connect(self.UpdataProgressBar_ReceiveFile)

        # --- 窗體美化 ---#
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )
        # ---------------#

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
        self.ui.button_SelectfFile.clicked.connect(self.SelectSendFile)
        self.ui.button_DownloadFile.clicked.connect(self.DownloadFile)

        # Setting 頁面按鈕事件 -----------------------------------------
        self.ui.button_OpenSaveFolder.clicked.connect(self.OpenSaveFolder)
        self.ui.button_SettingSave.clicked.connect(self.SettingSave)

    ###--- 各事件對應函數 ---###

    def MainClose(self):
        print(GUI, '關閉視窗!')
        self.close()

    def MainMinimized(self):
        print(GUI, '縮小視窗!')
        self.showMinimized()

    ### Client -----------------------------------------------------------------------------------------------------------

    def SwitchToClientPage(self):
        self.ui.stackedWidget.setCurrentIndex(0)  # 切換 Stack Widget 到 (索引值 0 / Client) 頁
        # self.ui.label_schedule.setText(str(0))

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

    ### Client 取件碼要求 header --------------------------------
    def ClientRequireFile(self):
        self.ui.progressBar_RecevieFile.setMaximum(100)  # 進度條最大值 100
        self.cFileLayoutVisible(False)  # 清空 client layout 避免要重複下載 連接時還顯示著上一個 header
        self.cFileDownloadVisible(False)
        self.ui.button_RequireFile.setEnabled(False)
        self.thread_ClientReceiveHeader.run = self.QThread_ClientReqHeader
        self.thread_ClientReceiveHeader.start()

    def QThread_ClientReqHeader(self):
        self.cFileLayoutVisible(False)  # 清空 client layout
        self.cFileDownloadVisible(False)
        self.ui.progressBar_RecevieFile.setValue(0) #進度條歸0

        boxKey = self.ui.input_PickupNumber.text()
        print('------------------')
        print('[Recv] start()')
        self.ui.button_RequireFile.setText('正在連接Server...')
        SUCCESS_START = client.start()
        if SUCCESS_START == False:
            print('[Recv] --Client connection fail.')
            self.ui.button_RequireFile.setText('連接失敗，重試')
            self.ui.button_RequireFile.setEnabled(True)
            self.thread_ClientReceiveHeader.quit()  # 掛起線程
            return
        self.ui.button_RequireFile.setText('連接成功')

        print('[Recv] reqBoxHeader()')
        SUCCESS_FOUND_HEADER = client.reqBoxHeader(boxKey)
        if SUCCESS_FOUND_HEADER == False:
            self.ui.button_RequireFile.setText('查無包裹')
            client.stop()
            self.ui.button_RequireFile.setEnabled(True)
            self.thread_ClientReceiveHeader.quit()  # 掛起線程
            return

        # client.stop() 
        self.ui.button_RequireFile.setText('再次查詢')
        ### GUI 顯示 檔案資料 ----------------------------------
        self.ui.label_cFilename.setText(str(client.box_name))
        self.ui.label_cFilesize.setText(str(sizeConverter(client.box_file_size / 1024)))
        self.cFileLayoutVisible(True)
        ### ---------------------------------------------------
        self.ui.button_RequireFile.setEnabled(True)
        self.thread_ClientReceiveHeader.quit()  # 掛起線程


    ### Client 取件碼下載檔案 --------------------------------
    def DownloadFile(self):
        self.cFileDownloadVisible(True) # 按下下載後顯示下載進度條
        self.ui.progressBar_RecevieFile.setStyleSheet("#progressBar_RecevieFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_RecevieFile::chunk { \n"
                                                    "background-color: rgb(170, 170, 255);\n"
                                                    "border-radius: 8px;\n"
                                                    "}")
        self.ui.button_DownloadFile.setEnabled(False) # 開始下載 button 禁用
        self.ui.button_RequireFile.setEnabled(False)

        self.thread_ClientReceiveFile.run = self.QThread_DownloadingFile
        self.thread_ClientReceiveFile.start()

    def QThread_DownloadingFile(self):
        #self.cFileLayoutVisible(False)  # 清空 client layout 避免要重複下載 連接時還顯示著上一個 header

        #client.start()
        boxKey = self.ui.input_PickupNumber.text()
        print('------------------')
        print('[Recv] reqBoxRecv()')
        client.reqBoxRecv(boxKey, self.DownloadProgressBarUpdate)
        #client.stop()

        self.ui.button_DownloadFile.setEnabled(True) # 下載結束 button 解鎖
        self.ui.button_RequireFile.setEnabled(True)
        self.thread_ClientReceiveHeader.quit()  # 掛起線程

    def UpdataProgressBar_ReceiveFile(self):
        progress = int(client.showDownloadProgress())
        #print('progress:',str(progress))

        if progress > 99:
            self.ui.progressBar_RecevieFile.setStyleSheet("#progressBar_RecevieFile{\n"
                                                        "border: 2px solid #000;\n"
                                                        "border-radius: 10px;\n"
                                                        "text-align:center;\n"
                                                        "}\n"
                                                        "#progressBar_RecevieFile::chunk { \n"
                                                        "background-color: rgb(0, 217, 0);\n"
                                                        "border-radius: 8px;\n"
                                                        "}")
        self.ui.progressBar_RecevieFile.setValue(progress)  # 增加進度條

    ### Server -----------------------------------------------------------------------------------------------------------

    def SwitchToServerPage(self):
        self.ui.stackedWidget.setCurrentIndex(1)  # 切換 Stack Widget 到 (索引值 1 / Server) 頁
        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Server,
                                  self.ui.button_Client,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

        # print(GUI, server.host + ' ' + str(server.port))

    def SelectSendFile(self):
        try:
            # 開啟資料夾，回傳型態為 tuple
            folder_path = QFileDialog.getOpenFileName(self,
                                                      'Open file',
                                                      './')  # start path
            file_name = os.path.basename(folder_path[0])
            file_size = os.path.getsize(folder_path[0]) / 1024  # 1024 byte = 1 kb

            print(GUI, 'folder_path: ', folder_path)
            print(GUI, 'file_name: ', file_name)
            print(GUI, 'file_size: ', file_size)
            client.setFile(folder_path[0])

            self.ui.label_Filename.setText(file_name)
            self.ui.progressBar_SendFile.setValue(0) #進度條歸0
            self.FileSizeConvert(file_size, self.ui.label_Filesize)  # 文件大小轉換，印出

            self.ui.button_Startlistening.setEnabled(True)
            self.sFileLayoutVisible(True)
            return
        except:
            print(GUI, '沒有選檔案@w@, 或是檔案類型錯誤')

    def FileSizeConvert(self, file_size, label: QtWidgets.QLabel):
        label.setText(sizeConverter(file_size))

    def StartListening(self):
        self.ui.progressBar_SendFile.setMaximum(100)  # 進度條最大值 100
        self.ui.progressBar_SendFile.setStyleSheet("#progressBar_SendFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_SendFile::chunk { \n"
                                                    "background-color: rgb(170, 170, 255);\n"
                                                    "border-radius: 8px;\n"
                                                    "}") # 進度條顏色
        self.ui.button_Startlistening.setEnabled(False)  # 開始發送 button 禁用
        self.ui.button_SelectfFile.setEnabled(False)  # 聆聽時選擇檔案 button 禁用

        self.thread_SendFile.run = self.QThread_SendFile
        self.thread_SendFile.start()

    def QThread_SendFile(self):
        self.sFileLayoutVisible(True)
        self.ui.button_Startlistening.setEnabled(True)

        print('------------------')
        print('[Send] start()')
        self.ui.button_Startlistening.setText('連接Server...')
        SUCCESS_START = client.start()
        if SUCCESS_START == False:
            print(GUI, '--Client connection fail.')
            self.ui.button_Startlistening.setEnabled(True)
            self.ui.button_SelectfFile.setEnabled(True)
            self.ui.button_Startlistening.setText('連接失敗')
            self.thread_SendFile.quit()  # 掛起線程
            return

        print('[Send] packingBox()')
        self.ui.button_Startlistening.setText('打包檔案中...')
        SUCCESS_PACKBOX = client.packingBox()
        if SUCCESS_PACKBOX == False:
            print(GUI, '--Client connection fail.')
            self.ui.button_Startlistening.setEnabled(True)
            self.ui.button_SelectfFile.setEnabled(True)
            self.ui.button_Startlistening.setText('打包失敗')
            self.thread_SendFile.quit()  # 掛起線程
            return

        print('[Send] reqBoxSend()')
        self.ui.button_Startlistening.setText('發送包裹中...')
        recvKey = client.reqBoxSend(self.UploadProgressBarUpdate)
        print('reqBoxSend() -> recvKey :', recvKey)

        ### 取件碼顯示 -------------------------------------------
        if recvKey == False:
            self.recvKeyList.append('\t寄件失敗')
        else:
            # tar_size 算出來最小都 10KB 起跳 我也不知為啥 client.py 的寫法跟 self.SelectSendFile() 的一樣 說不定是打包成tar後的鍋 反正能動先不管了
            self.recvKeyList.append(str('\t' + recvKey + '\t\t\t檔案大小 : ' + sizeConverter(client.tar_size / 1024)))

        self.ui.listWidget_Sendpackage.clear()
        self.ui.listWidget_Sendpackage.addItems(self.recvKeyList)
        ### -----------------------------------------------------

        client.stop()

        self.ui.button_Startlistening.setText('發送包裹') # 傳送完成了按鈕重置
        self.ui.button_Startlistening.setEnabled(True) # 開始發送 button 啟用
        self.ui.button_SelectfFile.setEnabled(True)  # 選擇檔案 button 啟用
        self.thread_SendFile.quit()  # 掛起線程

    def UpdataprogressBar_SendFile(self):
        progress = int(client.showUploadProgress())
        #print('progress:',str(progress))

        if progress > 99:
            self.ui.button_Startlistening.setText('接收取件碼中...')
            self.ui.progressBar_SendFile.setStyleSheet("#progressBar_SendFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_SendFile::chunk { \n"
                                                    "background-color: rgb(0, 217, 0);\n"
                                                    "border-radius: 8px;\n"
                                                    "}")
        """"""
        self.ui.progressBar_SendFile.setValue(progress) # 增加進度條

    ### Setting -----------------------------------------------------------------------------------------------------------

    def SwitchToSettingPage(self):
        self.ui.stackedWidget.setCurrentIndex(2)  # 切換 Stack Widget 到 (索引值 2 / Setting) 頁

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Setting,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_User)

    def SettingSave(self):
        while True:
            try:
                input_clientIP = self.ui.input_clientIP.text()
                input_clientPort = int(self.ui.input_clientPort.text())
                client.setHost(input_clientIP, input_clientPort)
                return
                '''if self.ui.input_ShowSavepath.text() == DEFAULT_SAVE_DIR:
                    QMessageBox.warning(self,
                                        '警告訊息',
                                        '請選擇保存路徑!\n',
                                        QMessageBox.Ok)
                    return

                

                QMessageBox.information(self,
                                        '提示訊息', '保存成功',
                                        QMessageBox.Ok)
                self.ui.button_Client.setEnabled(True)
                self.ui.button_Server.setEnabled(True)
                return'''
            except TypeError and ValueError:
                result = QMessageBox.warning(self,
                                             '參數錯誤',
                                             '請確認輸入正確的數值!\n'
                                             'IPv4 範例 192.168.1.10\n'
                                             'Port 範例 5000',
                                             QMessageBox.Ok)
                if result == QMessageBox.Ok:
                    print(GUI, 'TypeError or ValueError.')
                    return

    def OpenSaveFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self,
                                                       'Open folder',
                                                       './')  # start path

        client.setSaveFolder(folder_path)  # 設置 client 儲存路徑
        print(GUI, 'setSaveFolder() =', folder_path)
        self.ui.input_ShowSavepath.setText(folder_path)

    ### User -----------------------------------------------------------------------------------------------------------

    def SwitchToUserPage(self):
        self.ui.stackedWidget.setCurrentIndex(3)  # 切換 Stack Widget 到 (索引值 3 / User) 頁

        # 顏色轉換
        # button_union = [self.ui.button_User, self.ui.button_Client, self.ui.button_Server, self.ui.button_Setting]
        self.button_setStyleSheet(self.ui.button_User,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting)

    ### 滑鼠移動事件(拖動視窗實現) -----------------------------------------------------------------------------------------

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

    ### 奇怪的東西 --------------------------------------------------------------------------------------------------------

    def sFileLayoutVisible(self, flag):
        self.ui.label_Filesize.setVisible(flag)
        self.ui.label_Filename.setVisible(flag)
        self.ui.hint_Filesize.setVisible(flag)
        self.ui.hint_Filename.setVisible(flag)
        self.ui.hint_Sendschedule.setVisible(flag)
        self.ui.progressBar_SendFile.setVisible(flag)

        self.ui.Layout_FileInfo.setEnabled(flag)
        # self.ui.Layout_Filesize.setEnabled(flag)
        # self.ui.Layout_Filename.setEnabled(flag)

    def cFileLayoutVisible(self, flag):
        # self.ui.label_cFilesize.setVisible(flag)
        # self.ui.label_cFilename.setVisible(flag)
        self.ui.label_cFilename.setVisible(flag)
        self.ui.label_cFilesize.setVisible(flag)
        self.ui.hint_cFileize.setVisible(flag)
        self.ui.hint_cFilename.setVisible(flag)
        self.ui.button_DownloadFile.setVisible(flag)
        self.ui.Layout_cFileInfo.setEnabled(flag)

    def cFileDownloadVisible(self, flag):
        self.ui.hint_schedule.setVisible(flag)
        self.ui.progressBar_RecevieFile.setVisible(flag)

    def button_setStyleSheet(self, NowFocus: QtWidgets.QPushButton,
                             Other1: QtWidgets.QPushButton,
                             Other2: QtWidgets.QPushButton,
                             Other3: QtWidgets.QPushButton):

        otherPage_StyleSheet = 'background-color: rgba(36, 67, 124, 50);' \
                               'border-radius: 10px;' \
                               'color: rgb(255, 255, 255);'
        nowPage_StyleSheet = 'background-color: rgba(255, 255, 255, 255);' \
                             'border-radius: 10px;'

        NowFocus.setStyleSheet(nowPage_StyleSheet)
        Other1.setStyleSheet(otherPage_StyleSheet)
        Other2.setStyleSheet(otherPage_StyleSheet)
        Other3.setStyleSheet(otherPage_StyleSheet)




def sizeConverter(file_size):
    if file_size < 1024:
        return (str('%.2f' % file_size) + ' KB')
    elif file_size < 1024 * 1024:
        return (str('%.2f' % (file_size / 1024)) + ' MB')
    elif file_size < 1024 * 1024 * 1024:
        return (str('%.2f' % (file_size / 1024 / 1024)) + ' GB')
    else:
        return (str('%.2f' % (file_size / 1024 / 1024 / 1024)) + ' TB')