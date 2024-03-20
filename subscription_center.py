from PySide6.QtCore import QObject, Signal
from typing import Callable, Any

class NoArgs:
    pass

NOARGS = NoArgs()

class SubscriptionCenter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, ):
        self.manager = None

    def set_manager(self, manager_class):
        self.manager = manager_class()

    def register_signal(self, signal_name, signal):
        if not hasattr(self.manager, signal_name):
            setattr(self.manager, signal_name, signal)

    def register_signals(self, signals: dict[str, Signal]):
        for signal_name, signal in signals.items():
            self.register_signal(signal_name, signal)

    def subscribe(self, signal_name, slot_function):
        getattr(self.manager, signal_name).connect(slot_function)

    def unsubscribe(self, signal_name, slot_function):
        getattr(self.manager, signal_name).disconnect(slot_function)

    def publish(self, signal_name, data=NOARGS):
        if data is NOARGS:
            getattr(self.manager, signal_name).emit()
        else:
            getattr(self.manager, signal_name).emit(data)


class SingalsManager(QObject):
    main_window_message_submit = Signal(str)
    main_window_save_logs = Signal()
    main_window_scroll_to_bottom = Signal()
    bubble_set_deleted = Signal(str)
    api_reply_finished = Signal(dict)
    control_ask_ai = Signal(dict)
    control_create_bubbles = Signal(list)
    control_save_logs_finished = Signal()

subscription_center = SubscriptionCenter()
subscription_center.set_manager(SingalsManager)


class SubscriptionMixin:
    subscription_center = subscription_center


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_subscriptions()

    def init_subscriptions(self):
        pass

