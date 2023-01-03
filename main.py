# -*- coding: utf-8 -*-

import sys
from gui.controller import *


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = LoginWindow_controller()

    LoginWindow.show()
    sys.exit(app.exec_())