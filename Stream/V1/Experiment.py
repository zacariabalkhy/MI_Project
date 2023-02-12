import cv2
import threading
import time
from playsound import playsound
from datetime import datetime
import numpy as np
import json
from pylsl import StreamInlet, resolve_stream
import multiprocessing as mp
from threading import Thread
from time import sleep
import pandas as pd

class Experiment:
    def __init__(self, numTrials, trialLength, restLength, isMotorMovementExperiment):
        self.numTrials = numTrials
        self.trialLength = trialLength
        self.restLength = restLength
        self.dataStreamProcess = None
        self.experimentProcess = None
        self.EEGdata = []
        self.experimentMetaData = []  
        self.streamReady = False
        self.experimentComplete = False
        self.lastTimeStamp = 0
        self.trialSeparatedData = []
        self.sampleRate = 0
        self.isMotorMovementExperiment = isMotorMovementExperiment

    def beginExperimentAndCollectMetaData(self):
        while(not self.streamReady):
            sleep(1)
        experimentStartTime = datetime.now()
        
        #load experiment images
        if self.isMotorMovementExperiment:
            left = cv2.imread(".\\Resources\\move_left.png")
            right = cv2.imread(".\\Resources\\move_right.png")
        else:
            right = cv2.imread(".\\Resources\\think_right.png")
            left = cv2.imread(".\\Resources\\think_left.png")
        rest = cv2.imread(".\\Resources\\rest.png")

        #begin experiment loop
        for i in range(self.numTrials):
            dp = {}
            dp["trialNumber"] = i
            if i % 2 == 0:
                if self.isMotorMovementExperiment:
                    dp["trialType"] = "moveLeft"
                else:
                    dp["trialType"] = "thinkLeft"
                dp["trialStartTime"] = self.lastTimeStamp
                cv2.imshow("window", left)
                cv2.waitKey(self.trialLength * 1000)
                cv2.destroyAllWindows()
            else:
                if self.isMotorMovementExperiment:
                    dp["trialType"] = "moveRight"
                else:
                    dp["trialType"] = "thinkRight"
                dp["trialStartTime"] = self.lastTimeStamp
                cv2.imshow("window", right)
                cv2.waitKey(self.trialLength * 1000)
                cv2.destroyAllWindows()
            dp["trialEndTime"] = self.lastTimeStamp
            self.experimentMetaData.append(dp)

            #rest
            cv2.imshow("window", rest)
            cv2.waitKey(self.restLength * 1000)
            cv2.destroyAllWindows()
        self.experimentComplete = True

    def collectData(self):
        print("looking for an EEG stream...")
        streams = resolve_stream('type', 'EEG')
        if not streams or not streams[0]:
           return
        self.sampleRate = streams[0].nominal_srate()
        inlet = StreamInlet(streams[0], processing_flags=0)
        inlet.time_correction()
        self.streamReady = True
        while not self.experimentComplete:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample, timeStamp = inlet.pull_sample()
            self.lastTimeStamp = timeStamp + inlet.time_correction()
            # add time correction to get system local time, and append timestamp to data
            #timestamp += inlet.time_correction()
            if sample:
                sample.append(self.lastTimeStamp)
            self.EEGdata.append(sample)
    
    def runExperiment(self):
        self.dataStreamProcess = Thread(target=self.collectData)
        self.experimentProcess = Thread(target=self.beginExperimentAndCollectMetaData)
        self.dataStreamProcess.start()
        self.experimentProcess.start()
        self.experimentProcess.join()
        self.dataStreamProcess.join()
            
    def cleanAndSaveData(self, name):
        imageryOrMovement = "Imagery" if self.isMotorMovementExperiment else "Movement"
       
        # put eeg data into pandas df and pickle into a file
        columns = ["channel1", "channel2", "channel3", "channel4", "channel5", "channel6", "channel7", "channel8", "timestamp"]
        df = pd.DataFrame(self.EEGdata, columns=columns)
        df = df = df.apply(pd.to_numeric, errors='coerce') 
        df.to_pickle(".\\data\\" + name + imageryOrMovement + ".pkl")
        
        # write experiment metadata into a file
        file = open(".\\data\\" + name + imageryOrMovement + "Metadata.json", "w")
        file.write(json.dumps(self.experimentMetaData))
        file.close()
    
    def splitRawDataIntoTrials(self, df):
        trial = {}
        for i in range(len(self.experimentMetaData)):
            print(self.experimentMetaData[i])
            trial = self.experimentMetaData[i]
            trialStartTimeValMask = df["timestamp"] == float(trial["trialStartTime"])
            trialEndTimeValMask = df["timestamp"] == float(trial["trialEndTime"])
            trialStartIndex = df["timestamp"][trialStartTimeValMask].index.values[0]
            trialEndIndex = df["timestamp"][trialEndTimeValMask].index.values[0]
            trialDf = df.iloc[trialStartIndex:trialEndIndex,:]
            trialDf = trialDf.reset_index(drop=True)
            trial["data"] = trialDf
            self.trialSeparatedData.append(trial)
    



    
