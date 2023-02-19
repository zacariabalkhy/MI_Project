from EventClass import EventClass
from EventType import EventType
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager, NamespaceProxy
from time import sleep
import inspect

class ProxyBase(NamespaceProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')

class TestProxy(ProxyBase): pass

class MockEventClass(EventClass):
    def __init__(self):
        super().__init__()
        self.value = 0

    def onNotify(self, eventData: any, event: EventType) -> None:
        self.value = 1
        print("notified")

def register_proxy(name, cls, proxy, manager):
    for attr in dir(cls):
        if inspect.ismethod(getattr(cls, attr)) and not attr.startswith("__"):
            proxy._exposed_ += (attr,)
            setattr(proxy, attr, 
                    lambda s: object.__getattribute__(s, '_callmethod')(attr))
    manager.register(name, cls, proxy)

def runSubject(subject: MockEventClass):
        sleep(5)
        subject.notify(None, EventType.EXPERIMENTDATA)
        print("notifying")
        
def runObject(Object: MockEventClass):
    for i in range(10):
        sleep(1)
        print(Object.value)

def TwoInstanceEventTest():
    eventClass1 = EventClass()
    eventClass2 = EventClass()

    print("subscribing to 1 to 2")
    eventClass1.subscribeToSubject(eventClass2)
    print("sending message from 2 to 1")
    eventClass2.notify(None, EventType.EXPERIMENTDATA)
    print("unsubscribing 1 from 2")
    eventClass1.unsubscribeFromSubject(eventClass2)

    print("subscribing to 2 to 1")
    eventClass2.subscribeToSubject(eventClass1)
    print("sending message from 2 to 1")
    eventClass1.notify(None, EventType.SPATIALFILTER)
    print("unsubscribing 1 from 2")
    eventClass2.unsubscribeFromSubject(eventClass1)

def ThreeInstanceEventTest():
    eventClass1 = EventClass()
    eventClass2 = EventClass()
    eventClass3 = EventClass()

    print("subscribing to 1 and 2 to 3")
    eventClass1.subscribeToSubject(eventClass3)
    eventClass2.subscribeToSubject(eventClass3)
    print("sending message from 3")
    eventClass3.notify(None, EventType.EXPERIMENTDATA)
    print("unsubscribing 1 from 3")
    eventClass1.unsubscribeFromSubject(eventClass3)
    print("sending message from 3")
    eventClass3.notify(None, EventType.EXPERIMENTDATA)
    print("unsubscribing 2 from 3")
    eventClass2.unsubscribeFromSubject(eventClass3)

def CrossProcessEventTest():
    #BaseManager.register('MockEventClass', MockEventClass, TestProxy)
    manager = BaseManager()
    register_proxy('MockEventClass', MockEventClass, TestProxy, manager)

    manager.start()
    eventClass1 = manager.MockEventClass()
    eventClass2 = manager.MockEventClass()
    eventClass1.subscribeToSubject(eventClass2)

    eventClass2Process = Process(target=runSubject, args=[eventClass2])
    eventClass1Process = Process(target=runObject, args=[eventClass1])

    eventClass1Process.start()
    eventClass2Process.start()

    eventClass1Process.join()
    eventClass2Process.join()

    print (eventClass2.value)
    print (eventClass1.value)
if __name__ == "__main__":
    CrossProcessEventTest()

    

    

    

    

