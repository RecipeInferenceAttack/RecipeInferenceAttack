from allClass import *


def findEdge(edgeDict, deviceName, eventName, AttackEvent, flag):
    if flag == 1:
        # Trigger
        for k in edgeDict.values():
            if k.getType() == 1:
                continue
            if k.getStart().getName() == eventName and k.getStart().getDeviceName() == deviceName and k.getmaxWeight() > 0:
                AttackEvent.append(
                    k.getEnd().getName().replace('/', '&') + "/" + k.getEnd().getDeviceName() + "/" + str(k.getmaxWeight()))

    else:
        # Action
        for k in edgeDict.values():
            if k.getType() == 1:
                continue
            if k.getEnd().getName() == eventName and k.getEnd().getDeviceName() == deviceName and k.getmaxWeight() > 0:
                AttackEvent.append(
                    k.getStart().getName() + "/" + k.getStart().getDeviceName() + "/" + str(k.getmaxWeight()))


def AttackEvent(runNum):
    #logging.critical('Event Attack runNum: %d', runNum)
    AttackFilepath = currentDir() + os.sep + "Attack" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    Environmentfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    edgeDict = np.load(AttackFilepath + 'edgeDictCut.npy', allow_pickle=True).item()
    RulesDataset = np.load(Environmentfilepath + 'knowEvent.npy', allow_pickle=True).tolist()
    knownDevices = np.load(Environmentfilepath + 'knowDevicesList.npy', allow_pickle=True)
    deviceObjDict = np.load(Environmentfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    AttackEventList = []
    for i in RulesDataset:
        AttackEvent = []
        AttackEvent.append(i)
        deviceName = i.split('/')[0]
        eventName = i.split('/')[1]
        tmpDevice = deviceObjDict[deviceName]
        flag = 0
        triggerList = tmpDevice.getTrigger()
        triggerList2=[]
        for j in triggerList:
            triggerList2.append(j.getName())
        triggerList=triggerList2
        for j in triggerList:
            if j == eventName:
                # Trigger
                flag = 1
                break
        findEdge(edgeDict, deviceName, eventName, AttackEvent, flag)
        AttackEventList.append(AttackEvent)
    writeAttackPkl(AttackEventList, 'AttackEventList', runNum)
    writeAttackTxt(AttackEventList, 'AttackEventList', runNum)


if __name__ == '__main__':
    FileNum = 100
    for i in range(FileNum):
        AttackEvent(i)
