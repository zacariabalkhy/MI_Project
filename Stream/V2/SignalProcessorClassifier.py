from kafka import KafkaConsumer, KafkaProducer
from pylsl import StreamInfo, StreamInlet
import numpy as np
import json
class SignalProcessorClassifier:
    def __init__(self, decisionTopic: str, modelParamterTopic: str, kafkaServers: list, bufferLength: int, lslStream: StreamInfo):
        self.filters = None
        self.model = None
        self.consumer = None
        self.producer = None
        self.bufferLength = bufferLength
        self.decisionTopic = decisionTopic
        self.modelParamterTopic = modelParamterTopic
        self.kafkaServers = kafkaServers
        self.buffer = []
        self.lslStream = lslStream
        self.continueStreaming = True
        self.count = 0

    def __runClassificationPipeline__(self) -> int:
        rawDataArray = np.array(self.buffer)
        spectralFilteredArray = self.__spectralFilter__(rawDataArray)
        spatialFilteredArray = self.__spatialFilter__(spectralFilteredArray)
        return self.__classify__(spatialFilteredArray)

    def __checkForNewModelAndParameters__(self):
        currentParamerDict = self.consumer.poll(timeout_ms=0)
        if (currentParamerDict and len(currentParamerDict[self.modelParamterTopic]) != 0):
            print("singal:")
            print(currentParamerDict)
            self.filters = currentParamerDict[self.modelParamterTopic][0]['filters']
            self.model = currentParamerDict[self.modelParamterTopic][0]['model']

    def __spectralFilter__(self, rawData: np.array):
        return rawData

    def __spatialFilter__(self, data: np.array):
        return data

    def __classify__(self, data: np.array):
        self.count += 1
        return self.count % 2

    def InitializeAndRun(self):
        self.Initialize()
        self.Run()

    def Initialize(self):
        self.consumer = KafkaConsumer(self.modelParamterTopic, bootstrap_servers=self.kafkaServers, value_deserializer=lambda m: json.loads(m.decode('ascii')))
        self.producer = KafkaProducer(bootstrap_servers=self.kafkaServers, value_serializer=lambda m: json.dumps(m).encode('ascii'))
        topics = self.consumer.subscription()
        if topics:
            print(topics)
        else:
            print("not topics")

        #self.consumer.seek_to_end()
        self.__checkForNewModelAndParameters__()
        
    def Run(self):
        try:
            # create a new inlet to read from the stream
            #inlet = StreamInlet(self.lslStream)
            while self.continueStreaming:
                # first check for new model and parameters
                self.__checkForNewModelAndParameters__()

                # get a new sample (you can also omit the timestamp part if you're not
                # interested in it)
              #   sample, timestamp = inlet.pull_sample()

                # add time correction to get system local time, and append timestamp to data
              #  if timestamp:
              #      timestamp =  timestamp + inlet.time_correction()
              #  if sample:
              #      sample.append(timestamp)
              #  if len(self.buffer) == self.bufferLength:
              #      self.buffer.pop(0)
              #  self.buffer.append(sample)
                decision = self.__runClassificationPipeline__()
                self.producer.send(self.decisionTopic, decision)

        except KeyboardInterrupt as e:
            print("Stream reader stopped")
            raise e