import math
import random
from allClass import *


def attackEasyRule(runNum):
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('runNum: %d', runNum)

    # 读取配置文件
    npyfilepath = currentDir() + os.sep + "environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    randomDeviceList = np.load(npyfilepath + 'randomDeviceList.npy').tolist()
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    RulesList = np.load(npyfilepath + 'RulesList.npy', allow_pickle=True)
    RulesDataset = np.load(npyfilepath + 'easyRulesDataset.npy', allow_pickle=True)
    knowDevicesList = np.load(npyfilepath + 'knowDevicesList.npy', allow_pickle=True)
    randomRulesList = np.load(npyfilepath + 'randomRulesList.npy', allow_pickle=True)

    # Attack 1: generate event list 生成事件列表
    eventsDict = {}
    edgeDict = {}
    for i in randomDeviceList:
        for j in range(deviceObjDict[i].getTriggerNum()):
            eventsDict[i + '/' + deviceObjDict[i].getTrigger()[j].getName()] = Event(
                deviceObjDict[i].getTrigger()[j].getName(), i, 0)
        for j in range(deviceObjDict[i].getActionNum()):
            actionEvent = Event(deviceObjDict[i].getAction()[j].getName(), i, 1)
            triggeerNum = deviceObjDict[i].getAction()[j].getTriggerNum()
            aName = deviceObjDict[i].getAction()[j].getName()
            for k in range(triggeerNum):
                # actionEvent.addTrigger(deviceObjDict[i].getAction()[j].getTrigger()[k])
                tName = deviceObjDict[i].getAction()[j].getTrigger()[k].getName()
                tEage = Edge(i + '/' + aName, i + '/' + tName, 1, 1, i + '/' + aName + '/' + tName)
                edgeDict[i + '/' + aName + '/' + tName] = tEage
                actionEvent.addEdge(tEage)
            eventsDict[i + '/' + deviceObjDict[i].getAction()[j].getName()] = actionEvent
    writeAttackNpy(eventsDict, 'eventsDict', runNum)

    # Attack 2: generate edge list 生成边列表
    for i in RulesList:
        try:
            startEvent = eventsDict[i[4] + '/' + i[2]]
            endEvent = eventsDict[i[5] + '/' + i[3]]
        except:
            try:
                startEvent = eventsDict[i[5] + '/' + i[2]]
                endEvent = eventsDict[i[4] + '/' + i[3]]
            except:
                print('Attack 2 error edge')
                print(i)
                continue
        # 自触发权重为1
        if i[6] == '':
            weight = 1
        else:
            # sigmoid*2
            if i[6].find('k') != -1:
                popular = int(i[6].replace('k', '00').replace('.', ''))
            else:
                popular = int(i[6])
            weight = 2 / (1 + math.exp(-popular))
        edgeDict[i[0]] = Edge(startEvent, endEvent, weight, 0, i[0])
    writeAttackNpy(edgeDict, 'edgeDict', runNum)

    # Attack 3: update edge weight 更新边权重
    for i in RulesDataset:
        if i[4] in knowDevicesList:
            if i[5] in knowDevicesList:
                # both known
                flag = 0
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getStart().getDeviceName() == i[4] and j.getStart().getName() == i[2] \
                            and j.getEnd().getDeviceName() == i[5] and j.getEnd().getName() == i[3]:
                        j.addExecuteNum(1)
                        flag = 1
                        break

                if flag == 0:
                    try:
                        startEvent = eventsDict[i[4] + '/' + i[2]]
                        endEvent = eventsDict[i[5] + '/' + i[3]]
                    except:
                        try:
                            startEvent = eventsDict[i[5] + '/' + i[2]]
                            endEvent = eventsDict[i[4] + '/' + i[3]]
                        except:
                            print('Attack 3 error Rule')
                            print(i)
                            continue
                    if i[6] == '':
                        weight = 1
                    else:
                        if i[6].find('k') != -1:
                            popular = int(i[6].replace('k', '00').replace('.', ''))
                        else:
                            popular = int(i[6])
                        weight = 2 / (1 + math.exp(-popular))
                    edgeDict[i[4] + '/' + i[2] + '/' + i[5] + '/' + i[3]] = Edge(startEvent, endEvent, weight, 0, i[0])
                    edgeDict[i[4] + '/' + i[2] + '/' + i[5] + '/' + i[3]].addExecuteNum(1)
            else:
                # trigger known
                environment = []
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getStart().getDeviceName() == i[4] and j.getStart().getName() == i[2]:
                        environment.append(j)
                jNum = len(environment)
                for j in environment:
                    j.addExecuteNum(1 / jNum)
        else:
            if i[5] in knowDevicesList:
                # action known
                environment = []
                for j in edgeDict.values():
                    if j.getType() == 1:
                        continue
                    if j.getEnd().getDeviceName() == i[5] and j.getEnd().getName() == i[3]:
                        environment.append(j)
                jNum = len(environment)
                for j in environment:
                    j.addExecuteNum(1 / jNum)
            else:
                # both unknown
                continue
    writeAttackNpy(edgeDict, 'edgeDictUpdate', runNum)

    # Attack 4: output top-k edge list 输出边列表
    topkEdgeDict = {}
    maxweight = 0
    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight:
            maxweight = v.getmaxWeight()

    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight * topK:
            topkEdgeDict[k] = v
        else:
            v.setmaxWeight(0)

    topkEdgeList = []
    topkEdgeList2 = []
    for v in topkEdgeDict.values():
        topkEdgeList.append(v.getName())
        topkEdgeList2.append(v.getName() + '/' + str(v.getmaxWeight()))
    writeAttackTxt(topkEdgeList2, 'topkEdgeList', runNum)

    # Attack 5: output accuracy 输出准确率
    randomRulesNameList = []
    for i in randomRulesList:
        randomRulesNameList.append(i[0])
    randomRuleLen = len(randomRulesList)
    tp = 0
    fp = 0
    for i in topkEdgeList:
        if i in randomRulesNameList:
            tp += 1
        else:
            fp += 1
    accuracy = tp / randomRuleLen
    topkAccuracy = tp / (tp + fp)
    logging.critical('accuracy: ' + str(accuracy * 100) + '%')
    logging.critical('topkAccuracy: ' + str(topkAccuracy * 100) + '%')
    return accuracy, topkAccuracy


def findEdge(TN, TD, AN, AD, edgeDict, deviceObjDict, topkPathlen=5, maxDepth=3):
    TDT = deviceObjDict[TD].getTrigger()
    TDT2 = []
    for i in TDT:
        TDT2.append(i.getName())
    TDT = TDT2
    paths = []
    path = []

    if TN in TDT:
        # 第一项是Trigger
        for i in edgeDict.values():
            if i.getType() == 1:
                continue
            if i.getStart().getDeviceName() == TD and i.getStart().getName() == TN:
                # 一步到达
                if i.getEnd().getDeviceName() == AD and i.getEnd().getName() == AN:
                    i.addExecuteNum(1)
                    return 0
        dfsT(TN, TD, TN, TD, AN, AD, edgeDict, path, paths, 0, deviceObjDict, maxDepth)
    else:
        # 第一项是Action
        dfsA(TN, TD, TN, TD, AN, AD, edgeDict, path, paths, 0, deviceObjDict, maxDepth)

    pathsLen = len(paths)
    if pathsLen > topkPathlen:
        topkPath = []
        for i in paths:
            if len(topkPath) < topkPathlen:
                topkPath.append(i)
            else:
                def input(i, topkPath):
                    for j in topkPath:
                        if len(i) < len(j):
                            topkPath.remove(j)
                            topkPath.append(i)
                            input(j, topkPath)
                            break
                        if len(i) == len(j):
                            weighti = 0
                            weightj = 0
                            for k in range(len(i)):
                                weighti += i[k].getmaxWeight()
                                weightj += j[k].getmaxWeight()
                            if weighti > weightj:
                                topkPath.remove(j)
                                topkPath.append(i)
                                input(j, topkPath)
                                break


                input(i, topkPath)
        for i in topkPath:
            for j in i:
                j.addExecuteNum(0.2)

    else:
        for i in paths:
            for j in i:
                j.addExecuteNum(1 / len(paths))


def conditionJudge(tmpcondition, path, deviceObjDict):
    tmpDevice = tmpcondition.split('/')[0]
    tmpEvent = tmpcondition.split('/')[1]
    for i in path:
        oldCondition = i.getCondition()
        oldDevice = oldCondition.split('/')[0]
        oldEvent = oldCondition.split('/')[1]
        if oldDevice != tmpDevice:
            continue
        else:
            if oldEvent == tmpEvent:
                continue
            else:
                actionList = deviceObjDict[oldDevice].getAction()
                for j in actionList:
                    triggerList = j.getTrigger()
                    triggerList2 = []
                    for k in triggerList:
                        triggerList2.append(k.getName())
                    triggerList = triggerList2
                    if tmpEvent in triggerList:
                        if oldEvent in triggerList:
                            break
                        else:
                            return False

    return True


def dfsA(TN, TD, IN, ID, AN, AD, edgeDict, path=[], paths=[], depth=0, deviceObjDict={}, maxDepth=3):
    if IN == AN and ID == AD:
        paths.append(path.copy())
        return 0
    elif depth > maxDepth:
        return 0
    else:
        for i in edgeDict.values():
            if i.getType() == 0:
                continue
            if i.getStart().split('/')[0] == ID and i.getStart().split('/')[1] == IN:
                dfsT(TN, TD, i.getEnd().split('/')[1], i.getEnd().split('/')[0], AN, AD, edgeDict, path, paths, depth,
                     deviceObjDict, maxDepth)


def dfsT(TN, TD, IN, ID, AN, AD, edgeDict, path=[], paths=[], depth=0, deviceObjDict={}, maxDepth=3):
    if IN == AN and ID == AD:
        paths.append(path.copy())
    elif depth > maxDepth:
        return 0
    else:
        for i in edgeDict.values():
            if i.getType() == 1:
                continue
            if i.getStart().getDeviceName() == ID and i.getStart().getName() == IN:
                edge = i
                tmpcondition = i.getCondition()
                if tmpcondition is None:
                    path.append(edge)
                else:
                    if conditionJudge(tmpcondition, path, deviceObjDict):
                        path.append(edge)
                    else:
                        continue
                dfsA(TN, TD, i.getEnd().getName(), i.getEnd().getDeviceName(), AN, AD, edgeDict, path, paths, depth + 1,
                     deviceObjDict, maxDepth)
                path.pop()


def attackRule(runNum, topK, maxDepth=3, topkPath=5, ATWeight=10000, defaultWeight=1):
    logging.critical('ATTACK Rules runNum: %d', runNum)

    # 读取配置文件
    npyfilepath = currentDir() + os.sep + "environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    randomDeviceList = np.load(npyfilepath + 'randomDeviceList.npy').tolist()
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    RulesList = np.load(npyfilepath + 'RulesList.npy', allow_pickle=True).tolist()
    RulesDataset = []
    with open(npyfilepath + 'AttackDataset.pkl', 'rb') as f:
        RulesDataset = pickle.load(f)
    randomRulesList = np.load(npyfilepath + 'randomRulesList.npy', allow_pickle=True)

    # Attack 1: generate event list 生成事件列表
    eventsDict = {}
    edgeDict = {}
    for i in randomDeviceList:
        for j in range(deviceObjDict[i].getTriggerNum()):
            eventsDict[i + '/' + deviceObjDict[i].getTrigger()[j].getName()] = Event(
                deviceObjDict[i].getTrigger()[j].getName(), i, 0)
        for j in range(deviceObjDict[i].getActionNum()):
            actionEvent = Event(deviceObjDict[i].getAction()[j].getName(), i, 1)
            triggeerNum = deviceObjDict[i].getAction()[j].getTriggerNum()
            aName = deviceObjDict[i].getAction()[j].getName()
            for k in range(triggeerNum):
                # actionEvent.addTrigger(deviceObjDict[i].getAction()[j].getTrigger()[k])
                tName = deviceObjDict[i].getAction()[j].getTrigger()[k].getName()
                tEage = Edge(i + '/' + aName, i + '/' + tName, ATWeight, 1, i + '/' + aName + '/' + tName)
                edgeDict[i + '/' + aName + '/' + tName] = tEage
                actionEvent.addEdge(tEage)
            eventsDict[i + '/' + deviceObjDict[i].getAction()[j].getName()] = actionEvent
    #writeAttackNpy(eventsDict, 'eventsDict', runNum)

    # Attack 2: generate edge list 生成边列表
    for i in RulesList:
        try:
            startEvent = eventsDict[i[4] + '/' + i[2]]
            endEvent = eventsDict[i[5] + '/' + i[3]]
        except:
            try:
                startEvent = eventsDict[i[5] + '/' + i[2]]
                endEvent = eventsDict[i[4] + '/' + i[3]]
            except:
                print('Attack 2 error edge')
                print(i)
                continue
        # 自触发权重为1
        if i[6] == '':
            weight = defaultWeight
        else:
            # sigmoid*2
            if i[6].find('k') != -1:
                popular = int(i[6].replace('k', '00').replace('.', ''))
            else:
                popular = int(i[6])
            weight = 2 / (1 + math.exp(-popular))
        edgeDict[i[0]] = Edge(startEvent, endEvent, weight, 0, i[0])
    #writeAttackNpy(edgeDict, 'edgeDict', runNum)

    # Attack 3: update edge weight 更新边权重
    for data in RulesDataset:
        ActionNum = data[0]
        if ActionNum == 0:
            # Only One Event
            environment = []
            for edge in edgeDict.values():
                if edge.getType() == 1:
                    continue
                if edge.getStart().getDeviceName() == data[2] and edge.getStart().getName() == data[1]:
                    # Only Trigger
                    environment.append(edge)
                if edge.getEnd().getDeviceName() == data[2] and edge.getEnd().getName() == data[1]:
                    # Only Action
                    environment.append(edge)
            pathNum = len(environment)
            for path in environment:
                path.addExecuteNum(1 / pathNum)

        for j in range(ActionNum + 1):
            if j == 0:
                continue
            CurrentTrigger = data[2 * j - 1]
            CurrentTriggerDevice = data[2 * j]
            CurrentAction = data[2 * j + 1]
            CurrentActionDevice = data[2 * j + 2]
            findEdge(CurrentTrigger, CurrentTriggerDevice, CurrentAction, CurrentActionDevice,
                     edgeDict, deviceObjDict, topkPath, maxDepth)

    #writeAttackNpy(edgeDict, 'edgeDictUpdate', runNum)

    # Attack 4: output top-k edge list 输出边列表
    topkEdgeDict = {}
    maxweight = 0
    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight:
            maxweight = v.getmaxWeight()

    EdgeList = []
    for k, v in edgeDict.items():
        EdgeList.append(v.getName() + "/" + str(v.getmaxWeight()))
        if v.getmaxWeight() > maxweight * topK:
            topkEdgeDict[k] = v
        else:
            v.setmaxWeight(0)
    writeAttackTxt(EdgeList, 'EdgeList', runNum)

    topkEdgeList = []
    topkEdgeList2 = []
    for v in topkEdgeDict.values():
        topkEdgeList.append(v.getName())
        topkEdgeList2.append(v.getName() + '/' + str(v.getmaxWeight()))
    writeAttackTxt(topkEdgeList2, 'topkEdgeList', runNum)

    for i in edgeDict.values():
        if i.getName() not in topkEdgeList:
            i.setmaxWeight(0)
    writeAttackNpy(edgeDict, 'edgeDictCut', runNum)

    # Attack 5: output accuracy 输出准确率
    randomRulesNameList = []
    for i in randomRulesList:
        randomRulesNameList.append(i[0])
    randomRuleLen = len(randomRulesList)
    tp = 0
    fp = 0
    for i in topkEdgeList:
        if i in randomRulesNameList:
            tp += 1
        else:
            fp += 1
    accuracy = tp / randomRuleLen
    topkAccuracy = tp / (tp + fp)
    logging.critical('accuracy: ' + str(accuracy * 100) + '%')
    logging.critical('topkAccuracy: ' + str(topkAccuracy * 100) + '%')
    logging.critical('—————————————————————————————————————')

    return accuracy, topkAccuracy


def attackRuleC(runNum, topK, maxDepth=3, topkPath=5, ATWeight=10000, defaultWeight=1):
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('ATTACK Rules with condition runNum: %d', runNum)

    # 读取配置文件
    npyfilepath = currentDir() + os.sep + "environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    randomDeviceList = np.load(npyfilepath + 'randomDeviceList.npy').tolist()
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    RulesList = np.load(npyfilepath + 'RulesList.npy', allow_pickle=True).tolist()
    RulesDataset = []
    with open(npyfilepath + 'AttackDataset.pkl', 'rb') as f:
        RulesDataset = pickle.load(f)
    randomRulesList = np.load(npyfilepath + 'randomRulesList.npy', allow_pickle=True)

    # Attack 1: generate event list 生成事件列表
    eventsDict = {}
    edgeDict = {}
    for i in randomDeviceList:
        for j in range(deviceObjDict[i].getTriggerNum()):
            eventsDict[i + '/' + deviceObjDict[i].getTrigger()[j].getName()] = Event(
                deviceObjDict[i].getTrigger()[j].getName(), i, 0)
        for j in range(deviceObjDict[i].getActionNum()):
            actionEvent = Event(deviceObjDict[i].getAction()[j].getName(), i, 1)
            triggeerNum = deviceObjDict[i].getAction()[j].getTriggerNum()
            aName = deviceObjDict[i].getAction()[j].getName()
            for k in range(triggeerNum):
                # actionEvent.addTrigger(deviceObjDict[i].getAction()[j].getTrigger()[k])
                tName = deviceObjDict[i].getAction()[j].getTrigger()[k].getName()
                tEage = Edge(i + '/' + aName, i + '/' + tName, ATWeight, 1, i + '/' + aName + '/' + tName)
                edgeDict[i + '/' + aName + '/' + tName] = tEage
                actionEvent.addEdge(tEage)
            eventsDict[i + '/' + deviceObjDict[i].getAction()[j].getName()] = actionEvent
    #writeAttackNpy(eventsDict, 'eventsDict', runNum)

    # Attack 2: generate edge list 生成边列表
    for i in RulesList:
        try:
            startEvent = eventsDict[i[4] + '/' + i[2]]
            endEvent = eventsDict[i[5] + '/' + i[3]]
        except:
            try:
                startEvent = eventsDict[i[5] + '/' + i[2]]
                endEvent = eventsDict[i[4] + '/' + i[3]]
            except:
                print('Attack 2 error edge')
                print(i)
                continue
        # 自触发权重为1
        if i[6] == '':
            weight = defaultWeight
        else:
            # sigmoid*2
            if i[6].find('k') != -1:
                popular = int(i[6].replace('k', '00').replace('.', ''))
            else:
                popular = int(i[6])
            weight = 2 / (1 + math.exp(-popular))
        tmpDevice = deviceObjDict[random.choice(randomDeviceList)]
        triggerNum = tmpDevice.getTriggerNum()
        while triggerNum == 0:
            tmpDevice = deviceObjDict[random.choice(randomDeviceList)]
            triggerNum = tmpDevice.getTriggerNum()
        tmpTrigger = tmpDevice.getTrigger()[random.randint(0, tmpDevice.getTriggerNum() - 1)].getName()
        condition = tmpDevice.getName() + '/' + tmpTrigger
        edgeDict[i[0]] = Edge(startEvent, endEvent, weight, 0, i[0], condition)
    #writeAttackNpy(edgeDict, 'edgeDict', runNum)

    # Attack 3: update edge weight 更新边权重
    for data in RulesDataset:
        ActionNum = data[0]
        if ActionNum == 0:
            # Only One Event
            environment = []
            for edge in edgeDict.values():
                if edge.getType() == 1:
                    continue
                if edge.getStart().getDeviceName() == data[2] and edge.getStart().getName() == data[1]:
                    # Only Trigger
                    environment.append(edge)
                if edge.getEnd().getDeviceName() == data[2] and edge.getEnd().getName() == data[1]:
                    # Only Action
                    environment.append(edge)
            pathNum = len(environment)
            for path in environment:
                path.addExecuteNum(1 / pathNum)

        for j in range(ActionNum + 1):
            if j == 0:
                continue
            CurrentTrigger = data[2 * j - 1]
            CurrentTriggerDevice = data[2 * j]
            CurrentAction = data[2 * j + 1]
            CurrentActionDevice = data[2 * j + 2]
            findEdge(CurrentTrigger, CurrentTriggerDevice, CurrentAction, CurrentActionDevice,
                     edgeDict, deviceObjDict)

    #writeAttackNpy(edgeDict, 'edgeDictUpdate', runNum)

    # Attack 4: output top-k edge list 输出边列表
    topkEdgeDict = {}
    maxweight = 0
    for k, v in edgeDict.items():
        if v.getmaxWeight() > maxweight:
            maxweight = v.getmaxWeight()

    EdgeList = []
    for k, v in edgeDict.items():
        EdgeList.append(v.getName() + "/" + str(v.getmaxWeight()))
        if v.getmaxWeight() > maxweight * topK:
            topkEdgeDict[k] = v
        else:
            v.setmaxWeight(0)
    #writeAttackTxt(EdgeList, 'EdgeList', runNum)

    topkEdgeList = []
    topkEdgeList2 = []
    for v in topkEdgeDict.values():
        topkEdgeList.append(v.getName())
        topkEdgeList2.append(v.getName() + '/' + str(v.getmaxWeight()))
    writeAttackTxt(topkEdgeList2, 'topkEdgeList', runNum)

    for i in edgeDict.values():
        if i.getName() not in topkEdgeList:
            i.setmaxWeight(0)
    writeAttackNpy(edgeDict, 'edgeDictCut', runNum)

    # Attack 5: output accuracy 输出准确率
    randomRulesNameList = []
    for i in randomRulesList:
        randomRulesNameList.append(i[0])
    randomRuleLen = len(randomRulesList)
    tp = 0
    fp = 0
    for i in topkEdgeList:
        if i in randomRulesNameList:
            tp += 1
        else:
            fp += 1
    accuracy = tp / randomRuleLen
    topkAccuracy = tp / (tp + fp)
    logging.critical('Recall: ' + str(accuracy * 100) + '%')
    logging.critical('Precision: ' + str(topkAccuracy * 100) + '%')
    return accuracy, topkAccuracy


if __name__ == '__main__':
    # read parameters from config file  读取配置文件
    configfile = 'TAWFST.ini'
    parameters = readConfigFile(configfile)
    # DeviceListName = parameters['DeviceListName']
    # DeviceNumber = parameters['DeviceNumber']
    # RulesNumber = parameters['RulesNumber']
    # KnownDevicesNumber = parameters['KnownDevicesNumber']
    # DatasetLength = parameters['DatasetLength']
    topK = parameters['topK']
    # logpath = parameters['logpath']

    # # init logging 初始化日志
    # initlogging(logpath)
    # logging.critical('DeviceNumber: %d', DeviceNumber)
    # logging.critical('RulesNumber: %d', RulesNumber)
    # logging.critical('knowDevicesNumber: %d', KnownDevicesNumber)
    # logging.critical('DatasetLength: %d', DatasetLength)

    # runNum = 100
    # finalAccuracy = 0
    # finalTopkAccuracy = 0
    # for i in range(runNum):
    #     a, ta = attackRule2(i,topK)
    #     finalAccuracy += a
    #     finalTopkAccuracy += ta
    # finalAccuracy /= runNum
    # finalTopkAccuracy /= runNum
    # logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    # logging.critical('finalAccuracy: ' + str(finalAccuracy * 100) + '%')
    # logging.critical('finalTopkAccuracy: ' + str(finalTopkAccuracy * 100) + '%')

    attackRule(0, topK)
