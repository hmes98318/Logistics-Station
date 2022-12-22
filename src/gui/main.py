from PyQt5 import QtWidgets, QtCore
from controller import LoginWindow_controller, MainWindow_controller

# testing
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = LoginWindow_controller()
    LoginWindow.show()
    sys.exit(app.exec_())
