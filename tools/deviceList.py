import numpy as np

deviceList = ['nuki','hue','date_and_time','wemo_switch','mycurtains','hue','arlo','weather','tado_air_conditioning','nest_protect','arlo','location']

filename = open('deviceList2.txt', 'w')
for value in deviceList:
    filename.write(str(value))
    filename.write(',')
filename.close()

deviceList = np.array(deviceList)
np.save('deviceList2.npy', deviceList)