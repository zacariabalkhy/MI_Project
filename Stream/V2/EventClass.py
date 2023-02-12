from __future__ import annotations #needed for class self reference in addObserver and removeObserver
from EventType import EventType
from collections import deque

class EventClass:
    def __init__(self):
        self.observers = deque()
        self.subjects = deque()

    def __del__(self):
        for subject in self.subjects:
            subject.removeObserver(self)
    
    def subscribeToSubject(self, subject: EventClass) -> None:
        self.subjects.append(subject)
        subject.addObserver(self)
    
    def unsubscribeFromSubject(self, subject: EventClass) -> None:
        self.subjects.remove(subject)
        subject.removeObserver(self)
        
    def onNotify(self, eventData: any, event: EventType ) -> None:
        return
    
    def addObserver(self, observer: EventClass) -> None:
        self.observers.append(observer)

    def removeObserver(self, observer: EventClass) -> None:
        self.observers.remove(observer)
    
    def notify(self, eventData: any, event: EventType) ->None:
        for observer in self.observers:
            observer.onNotify(eventData, event)


