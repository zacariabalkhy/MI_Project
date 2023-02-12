from os import times
from pylsl import StreamInlet, resolve_stream
from datetime import datetime
from StreamReader import StreamReader
from Classifier import Classifier
import pandas as pd
from Experiment import Experiment
import time
import json
import os
import Filter
from sklearn import preprocessing
import numpy as np
from sklearn.decomposition import FastICA
from scipy.linalg import eigh 
import plot
import math


def loadDf(fileName):
    return pd.read_pickle(fileName)

def loadExpMetaData(fileName):
    trialData = []
    with open(fileName, 'r') as file:
        trialData = json.load(file)
    return trialData

"""
Input: 
      - df : raw data from session
      - metadata : data tracking trial types and timestamps from the experiment
Operation:
      - splits the raw session data into trials 
      - all right handed trials are filled first
      - there are an equal number of trials 
Returns:
        - data in a NumTrials x NumSamples x NumChannels numpy array
"""
def splitRawDataIntoTrialsByType(df, metaData):
    rightTrials = []
    leftTrials = []
    for i in range(len(metaData)):
        trial = metaData[i]
        trialStartTimeValMask = df["timestamp"] == float(trial["trialStartTime"])
        trialStartIndex = df["timestamp"][trialStartTimeValMask].index.values[0]
        # make trial end time = trialStartTime + trialLength, so that we standardize triallengths
        # trial length is 1250 = 5 sec * 250 Hz
        trialEndIndex = trialStartIndex + 1250 
        trialDf = df.iloc[trialStartIndex:trialEndIndex,:]
        trialDf = trialDf.reset_index(drop=True)
        trialDf.drop('timestamp', axis=1, inplace=True) # no longer need timestamp
        if trial["trialType"] == "moveRight":
            rightTrials.append(trialDf)
        elif trial["trialType"] == "moveLeft":
            leftTrials.append(trialDf) 
    rightTrialsArray = np.array(rightTrials)
    leftTrialsArray = np.array(leftTrials)
    allData = np.concatenate((rightTrialsArray, leftTrialsArray))
    return allData

"""
Input: 
      - arr : numpy array containing raw session data
      - refChannel : eyeblink reference channel.
Operation:
      - performs ICA on the incoming channel
      - zeros the resultant channel that is most similar to the reference channel
      - performs inverse ICA to regain original source signal
Returns:
        - reconstructed signal source
"""
def removeEyeBlinkArtifacts(arr, refChannel):
    ica = FastICA(n_components=8)
    ica.fit(arr)
    components = ica.transform(arr)
    # subtract each component from the first channel and then take the power of the result (sum of each squared sample)
    # the component with the lowest resulting power should correspond to the "eye-blink" signal.
    # make this component 0s and then do an invers ICA transform
    eyeBlinkComponent = -1
    eyeBlinkComponetPower = 0
    i = 0
    for component in components.T:
        compDiff = arr.T[refChannel] - component
        compDiff = np.square(compDiff)
        compPower = np.sum(compDiff, 0) 
        if eyeBlinkComponent == -1 or compPower < eyeBlinkComponetPower:
            eyeBlinkComponetPower = compPower
            eyeBlinkComponent = i
        i+=1
    components = components.T
    components[eyeBlinkComponent] = 0
    components = components.T
    reconstructed = ica.inverse_transform(components)
    arr = reconstructed
    return arr
    
"""
Input: 
    - channel : signal to filter
Operation:
    - applies 2-250 hz bandpass and band stop around 60 hz to eliminate powerline noise
Returns:
    - filtered signal
"""
def filterChannel(channel):
    bandpassed = Filter.butter_bandpass_filter(channel, 2, 10, 250, 1)
    bandstopped = Filter.butter_bandstop_filter(bandpassed, 59, 61, 250, 1)
    return bandstopped

"""
Input: 
    - arr : multicahnnel input siganl
Operation:
    - applies 2-250 hz bandpass and band stop around 60 hz bandstop on each channel in the source signal
Returns:
    - filtered signal
"""
def filterData(arr):
    channelBySampleArray = arr.T
    numChannels = channelBySampleArray.shape[0]
    for i in range(numChannels):
        channelBySampleArray[i] = filterChannel(channelBySampleArray[i])
    return channelBySampleArray.T

"""
Input:
    - datadir : path to directory with experimental data
    - subjectName: name of subject to grab data for
Operation:
    - reads raw and meta data into memory
    - applies spectral filter on raw data and removes eyeblinks
    - splits data into trials
Returns:
    - list of np data arrays one for each trial subject
"""
def loadAndFilterPatientData(datadir, subjectName):
    subjects = os.listdir(datadir)
    dataPerSubject = []
    for subject in subjects:
        if subject == subjectName:
            subjectDir = datadir + "/" + subject 
            df = loadDf(subjectDir + "/" + subject + "Imagery.pkl")
            metaData = loadExpMetaData(subjectDir + "/" + subject + "ImageryMetadata.json")

            dfNoTimeStamp = df.drop(["timestamp"], axis=1)
            dataArray = dfNoTimeStamp.to_numpy()
            nonTimeStampColumns = list(dfNoTimeStamp.columns.values)
            
            dataArray = filterData(dataArray)
            dataArray = removeEyeBlinkArtifacts(dataArray, 0)

            newDf = pd.DataFrame(dataArray, columns=nonTimeStampColumns)
            newDf = newDf.assign(timestamp=df[:]["timestamp"])

            data = splitRawDataIntoTrialsByType(newDf, metaData)
            dataPerSubject.append(data)
            break
    return dataPerSubject

"""
Input: 
    - arr : array to estimate covariance of, in this case a timeseries of EEG data
Operation:
    - calculate to covariance of the matrix !
Returns:
    - covariance matrix
"""
def calculateCovarianceEstimate(arr):
    # covariance matrix is numChannels x numChannels
    covar = np.zeros(shape=(arr.shape[2], arr.shape[2]))
    numTrials = arr.shape[0]
    for trial in arr:
        covar += np.matmul(trial.T,trial)
    covar += 1/numTrials
    return covar

"""
Input:
    - A : matrix 1
    - B: matrix 2
Operation:
    - Calculates the generalized eigenvectors/values for A with respect to B
Returns:
    - list of eigen values and vectors, sorted by eigenvalue 
"""
def calculateGeneralizedEigenVectors(A, B):
    eigvals, eigvecs = eigh(A, B, eigvals_only=False)
    return eigvals, eigvecs

"""
Input:
    - eigvecs: list of eigenvectors
    - halfNumFilters: half the number of filtered channels we want (6)
Operation:
    - creates W filter for the incoming source signal
Returns: 
    - filter ! 
"""
def createFilter(eigvecs, halfNumFilters):
    filterCollector = []
    for i in range(len(eigvecs)):
        if (i < halfNumFilters or i >= len(eigvecs) - halfNumFilters):
            filterCollector.append(eigvecs[i])
    return np.array(filterCollector)

"""
Input:
    - filter: W filter 
    - arr: half the number of filtered channels we want (6)
Operation:
    - creates W filter for the incoming source signal
Returns: 
    - filter ! 
"""
def applySpatialFilter(filter, arr):
    return np.matmul(filter, arr)
    
if __name__ == "__main__":
    dataPerSubject = loadAndFilterPatientData("C:/OpenBCI/MI_Project/Src/Stream/data")
    
    for subjectData in dataPerSubject:
        scaler = preprocessing.StandardScaler()
        num_instances, num_time_steps, num_features = subjectData.shape
        subjectData = np.reshape(subjectData, newshape=(-1, num_features))
        subjectData = scaler.fit_transform(subjectData)
    
        subjectData = np.reshape(subjectData, newshape=(num_instances, num_time_steps, num_features))
        
        rightCovar = calculateCovarianceEstimate(subjectData[:30])
        leftCovar = calculateCovarianceEstimate(subjectData[30:])
        eigvals, eigvecs = calculateGeneralizedEigenVectors(rightCovar, leftCovar)
        
        for eigval in eigvals:
            print(eigval)
        for eigvec in eigvecs:
            print(eigvec)
        filter = createFilter(eigvecs, 3)
        print(filter.shape)
        print(filter)
        
        #for i in range(subjectData.shape[0]):
         #   plotTimeSeriesNpArray(subjectData[i][:][:])   