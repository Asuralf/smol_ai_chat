import os
import datetime
import uuid
import json


# model

class ChatMessage:
    def __init__(self, sender, message,) -> None:

        # data model
        self._uuid = str(uuid.uuid4())
        self._created_at = datetime.datetime.now()
        self.updated_at = None
        self._sender = sender
        self.message = message
        self.is_deleted = False

    @property
    def uuid(self):
        return self._uuid

    @property
    def sender(self):
        return self._sender

    @property
    def created_at(self):
        return self._created_at

    # serialization / deserialization
    @classmethod
    def from_dict(cls, d):
        msg_obj = cls(d['sender'], d['message'])
        msg_obj._uuid = d['uuid']
        msg_obj._created_at = datetime.datetime.strptime(d['created_at'], "%Y-%m-%d %H:%M:%S")
        msg_obj.updated_at = datetime.datetime.strptime(d['updated_at'], "%Y-%m-%d %H:%M:%S") if d['updated_at'] else None
        msg_obj.is_deleted = d['is_deleted']

        return msg_obj

    def to_dict(self):
        return {
            'uuid':         self.uuid,
            'created_at':   self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at':   self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            'sender':       self.sender,
            'message':      self.message,
            'is_deleted':   self.is_deleted,
        }


class ChatLogs:

    def __init__(self, json_path, ):
        self.json_path = json_path
        self.chat_messages = self.load_messages(json_path)

    def create_message(self, sender, message):
        msg_obj = ChatMessage(sender, message)
        self.chat_messages[msg_obj.uuid] = msg_obj
        return msg_obj

    def load_messages(self, json_path):
        log_dicts = self.load_json(json_path)
        chat_messages = {}
        for d in log_dicts:
            msg_obj = ChatMessage.from_dict(d)
            chat_messages[msg_obj.uuid] = msg_obj
        return chat_messages

    def load_json(self, json_path):
        if os.path.exists(json_path):
            with open(json_path, 'r+', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []

    def save(self,):
        with open(self.json_path, 'w+', encoding='utf-8') as f:
            json.dump([msg_obj.to_dict() for uuid, msg_obj in self.chat_messages.items()], f, indent=2, ensure_ascii=False)

    def __getitem__(self, uuid):
        return self.chat_messages[uuid]
    
    def __setitem__(self, uuid, value):
        self.chat_messages[uuid] = value
