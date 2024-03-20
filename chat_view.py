import os

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QMenu
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QIcon

from subscription_center import SubscriptionMixin


# view
class ChatBubble(QWidget, SubscriptionMixin):

    def __init__(self, uuid: str, sender: str, message: str):
        super().__init__()

        # data
        self.uuid = uuid
        self.sender = sender
        self.message = message

        self.render()

    # methods
    def render(self, ):

        # label
        self.label = QLabel('')
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            "border: 1px solid gray; border-radius: 10px; padding: 5px; margin: 1px;"
        )
        self.update_text()

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.menu = QMenu(self)
        self.menu.addAction("转发")
        self.menu.addAction("复制").triggered.connect(self.slot_copy_text_to_clipboard)
        self.menu.addAction("删除").triggered.connect(self.slot_delete_message)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_text(self):
        self.label.setText(f"<b>{self.sender}:</b><br />{self.message}")

    def show_context_menu(self, pos):
        self.menu.exec(self.mapToGlobal(pos))

    def get_bubble_vertical_position(self, chat_logs_layout):
        index = chat_logs_layout.indexOf(self)
        if index != -1:
            item = chat_logs_layout.itemAt(index)
            widget_geometry = item.geometry()
            return widget_geometry.y()
        else:
            return None

    # internal slots
    def slot_copy_text_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.message.replace('<br />', '\n'))

    def slot_delete_message(self):
        self.subscription_center.publish('bubble_set_deleted', self.uuid)
        self.setParent(None)
        self.deleteLater()


class ChatWidget(QWidget, SubscriptionMixin):

    def __init__(self):
        super().__init__()

        # self.chat_log = ChatLogs('./chat_log.json')                 # {uuid: messege}
        self.init_ui()
        # 使用定时器调用滚动到底部方法
        self.scroll_to_bottom()

    def init_ui(self):

        self.setWindowTitle('AI Chat')
        app_icon = QIcon(os.path.abspath('icon.png'))
        self.setWindowIcon(app_icon)

        self.chat_history_layout = QVBoxLayout()
        self.chat_history_layout.setSpacing(0)
        self.chat_history_layout.addStretch()

        self.chat_logs_widget = QWidget()
        self.chat_logs_widget.setLayout(self.chat_history_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_logs_widget)

        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(100)
        self.input_box.textChanged.connect(self.slot_check_input_content)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.slot_submit_message)

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.input_box)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.send_button)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        # event
        self.close_event = None

        # bubbles
        self.bubbles: dict[str, ChatBubble] = {}

    # methods
    def submit_message(self,):
        plain_text = self.input_box.toPlainText().strip()
        # self.signal_message_submit.emit(plain_text)
        self.input_box.clear()
        self.subscription_center.publish('main_window_message_submit', plain_text)

    # internal slots
    @Slot()
    def slot_check_input_content(self, ):
        plain_text = self.input_box.toPlainText()
        if len(plain_text.strip()) > 0 and plain_text[-1] == '\n':
            self.submit_message()

    @Slot()
    def slot_submit_message(self):
        self.submit_message()

    # slots
    def slot_create_bubbles(self, chat_messages: list):
        # create bubbles
        for chat_message_dict in chat_messages:
            bubble = ChatBubble(uuid=chat_message_dict['uuid'], sender=chat_message_dict['sender'], message=chat_message_dict['message'].replace("\n", '<br />'))
            self.bubbles[chat_message_dict['uuid']] = bubble
            bubble.update_text()
            self.chat_history_layout.insertWidget(self.chat_history_layout.count() - 1, bubble)
        self.subscription_center.publish('main_window_scroll_to_bottom')

    def slot_save_logs_finished(self):
        self.close_event.accept()

    def slot_update_bubble_message(self, reply: dict):
        message_uuid = reply['uuid']
        message = reply['message']
        error = reply['error'] 

        bubble = self.bubbles[message_uuid]
        if error == '':
            bubble.message = message.replace("\n", '<br />')
        else:
            bubble.message = error.replace("\n", '<br />')
        bubble.update_text()

        self.subscription_center.publish('main_window_scroll_to_bottom')

    # events
    def closeEvent(self, event):
        # 在窗口关闭前执行特定操作，比如保存数据
        self.close_event = event
        self.subscription_center.publish('main_window_save_logs')

    # view methods
    def _scroll_to_vpos(self, vpos: str|int ='max'):
        scrollbar = self.scroll_area.verticalScrollBar()
        if vpos == 'max':
            scrollbar.setValue(scrollbar.maximum())

    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def scroll_to_bottom(self):
        QTimer.singleShot(500, self._scroll_to_bottom)

    def scroll_to_pos(self, pos):
        QTimer.singleShot(500, lambda :self._scroll_to_vpos(pos))

    # subscriptions
    def init_subscriptions(self):
        self.subscription_center.subscribe('control_create_bubbles', self.slot_create_bubbles)
        self.subscription_center.subscribe('control_save_logs_finished', self.slot_save_logs_finished)
        self.subscription_center.subscribe('api_reply_finished', self.slot_update_bubble_message)
        self.subscription_center.subscribe('main_window_scroll_to_bottom', self.scroll_to_bottom)



