from SignalProcessor import SignalProcessor
from EventType import EventType

if __name__ == "__main__":
    eventClass1 = SignalProcessor()
    eventClass2 = SignalProcessor()
    eventClass3 = SignalProcessor()

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

    

