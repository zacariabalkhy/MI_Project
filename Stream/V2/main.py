from pongGame.pong import Pong
from SignalProcessorClassifier import SignalProcessorClassifier
from pylsl import resolve_stream
from multiprocessing import Process
import pygame

if __name__ == "__main__":

    pygame.init()
    
    streams = []# resolve_stream('type', 'EEG')
    if not streams or not streams[0]:
        print('no stream, quitting')
    #else:
    pong = Pong('decisionTopic', ['[::1]:9092'])
    signalProcessorClassifier = SignalProcessorClassifier('decisionTopic', 
                                'modelParameterTopic', ['[::1]:9092'], 250*3, None)

    a = Process(target=signalProcessorClassifier.InitializeAndRun)
    b = Process(target=pong.InitializeAndRun)
    a.start()
    b.start()
    a.join()
    b.join()

    #pongProcess = Process(target=pong.InitializeAndRun())
    #ignalProcessorClassifierProcess = Process(signalProcessorClassifier.InitializeAndRun())

    #signalProcessorClassifierProcess.start()
    #pongProcess.start()

    #signalProcessorClassifierProcess.join()
     #pongProcess.join()


