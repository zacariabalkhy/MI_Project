from EventClass import EventClass
from EventType import EventType
from time import sleep
class SignalProcessor(EventClass):
    def __init__(self):
        self.filters = []
        super().__init__()

    def onNotify(self, eventData: any, event: EventType) -> None:
        if event == EventType.SPATIALFILTER:
            self.filters = eventData
    
    