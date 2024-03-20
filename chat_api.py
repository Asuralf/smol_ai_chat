import json

from PySide6.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PySide6.QtCore import QObject, QUrl


class ChatAPIBase(QObject):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.apk_key = self.load_api_key()
        self.api_url = f"https://api.a20safe.com/api.php?api=51&key={self.apk_key}&text="

        # network
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.slot_finished_asking)

    def load_api_key(self):
        with open('api_config.json', 'r') as f:
            return json.load(f)['API_KEY']

    def fetch_json(self, url):
        request = QNetworkRequest(QUrl(url))
        self.manager.get(request)

    def resovlve_ai_json(self, json_data):
        json_data = json.loads(json_data)
        if json_data['code'] == 0:
            reply = json_data['data'][0]['reply']
        else:
            reply = str(json_data)
        return reply

    # internal slots
    def slot_finished_asking(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            # Decode the JSON data
            json_data = data.data().decode('utf-8')
            json_reply_data = self.resovlve_ai_json(json_data)

            message_uuid = reply.url().toString().split('&uuid=')[1]
            message = json_reply_data.strip()

            reply_dict = {
                'uuid': message_uuid,
                'message': message,
                'error': '',
            }

        else:
            reply_dict = {
                'uuid': message_uuid,
                'message': message,
                'error': reply.errorString(),
            }
            print("Error occurred:", reply.errorString())

        reply.deleteLater()

        return reply_dict
