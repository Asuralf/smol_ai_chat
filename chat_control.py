import datetime
from PySide6.QtCore import QObject
from PySide6.QtNetwork import QNetworkReply

from subscription_center import SubscriptionMixin
from chat_api import ChatAPIBase
from chat_data import ChatLogs


class ChatAPI(ChatAPIBase, SubscriptionMixin):

    def slot_finished_asking(self, reply: QNetworkReply):
        reply_dict = super().slot_finished_asking(reply)
        self.subscription_center.publish('api_reply_finished', reply_dict)

    # slot
    def slot_ask_ai(self, message_dict):
        message = message_dict['message']
        ai_message_uuid = message_dict['ai_message_uuid']
        url = self.api_url + str(message) + f'&uuid={ai_message_uuid}'
        self.fetch_json(url)

    def init_subscriptions(self):
        self.subscription_center.subscribe('control_ask_ai', self.slot_ask_ai)


# control
class ChatController(QObject, SubscriptionMixin):

    def __init__(self, chat_logs: ChatLogs, parent=None) -> None:
        super().__init__(parent)

        # data
        self.chat_logs = chat_logs

        # api
        self.chat_api = ChatAPI()

        # init
        messages_list = [
            message.to_dict() for message in self.chat_logs.chat_messages.values() if not message.is_deleted
        ]
        self.subscription_center.publish('control_create_bubbles', messages_list)


    # Slots
    def slot_message_accept(self, message: str):
        # create_messages
        you_message = self.chat_logs.create_message('You', message)
        ai_message = self.chat_logs.create_message('AI', '...')

        # use api
        # self.chat_api.ask_ai(you_message.message, you_message.uuid)
        # update ui
        self.subscription_center.publish('control_create_bubbles', [
            you_message.to_dict(),
            ai_message.to_dict(),
        ])

        ask_dict = you_message.to_dict()
        ask_dict['ai_message_uuid'] = ai_message.uuid
        self.subscription_center.publish('control_ask_ai', ask_dict)


    def slot_reply_finished(self, reply: dict):
        """
        reply: {
            uuid: str,
            message: str,
            error: str,
        }
        """
        # update data
        chat_message = self.chat_logs[reply['uuid']]
        if reply['error'] == '':
            chat_message.message = reply['message']
        else:
            chat_message.message = f'error: ' + reply['error']
        chat_message.updated_at = datetime.datetime.now()

    def slot_save_logs(self):
        # 执行保存操作的逻辑
        self.chat_logs.save()
        self.subscription_center.publish('control_save_logs_finished')

    def slot_delete_message(self, message_uuid: str):
        self.chat_logs[message_uuid].is_deleted = True

    # subscriptions
    def init_subscriptions(self):
        self.subscription_center.subscribe('main_window_message_submit', self.slot_message_accept)
        self.subscription_center.subscribe('api_reply_finished', self.slot_reply_finished)
        self.subscription_center.subscribe('main_window_save_logs', self.slot_save_logs)
        self.subscription_center.subscribe('bubble_set_deleted', self.slot_delete_message)