from EventClass import EventClass
from EventType import EventType

class SignalProcessor(EventClass):
    def __init__(self):
        self.filters = []
        super().__init__()

    def onNotify(self, eventData: any, event: EventType) -> None:
        print(event)
    