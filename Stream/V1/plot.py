import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plotTimeseries(df):
    channels = list(df.columns.values)
    plt.figure(figsize=(10,10))
    i = 1
    for col in channels:
        if "channel" in col:
            plt.subplot(9, 1, i)
            plt.plot(df[:]['timestamp'], df[:][col], "b")
            plt.xlabel('Sample')
            plt.ylabel('Amplitude')
            plt.tight_layout()
            i+=1
    plt.show()

def plotTimeSeriesNpArray(arr):
    arrT = arr.T
    plt.figure(figsize=(10,10))
    for i in range(arrT.shape[0]):
        x_axis = np.arange(0, arrT[i].shape[0])
        plt.subplot(9, 1, i + 1)
        plt.plot(x_axis, arrT[i], "b")
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')
        plt.tight_layout()
    plt.show()