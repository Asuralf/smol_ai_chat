import sys

from PySide6.QtWidgets import QApplication

from chat_view import ChatWidget
from chat_control import ChatController
from chat_data import ChatLogs


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ChatWidget()
    main_window.resize(600, 900)
    main_window.show()
    controller = ChatController(ChatLogs('./chat_log.json'), main_window)

    sys.exit(app.exec())