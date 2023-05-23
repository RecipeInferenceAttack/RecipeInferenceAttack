import logging
import math
import os
import pickle
import random

from sklearn import tree, ensemble, neural_network,metrics
from sklearn.model_selection import train_test_split

from allClass import *
import numpy as np


def AttackStates(runNum, datasetLen, scoreList, kdn):
    logging.critical('ML Attack States runNum: %d', runNum)
    modelPath = "Model" + os.sep + str(runNum) + os.sep
    npyPath = "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    TriggerDeviceList = np.load(npyPath + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    MLLabel = np.load(npyPath + 'MLLabel.npy', allow_pickle=True).tolist()
    deviceObjDict = np.load(npyPath + 'deviceObjDict.npy', allow_pickle=True).item()
    deviceStateDict = {}
    for device in TriggerDeviceList:
        deviceStateDict[device] = deviceObjDict[device].getStateNum()
    logging.critical('——————————————————————————')
    localScoreList = [0 for i in range(len(scoreList))]
    for targetDeviceNum in range(kdn, len(TriggerDeviceList)):
        MLdataset = []
        targetDevice = TriggerDeviceList[targetDeviceNum]
        logging.critical('targetDevice: %s', targetDevice)
        for i in range(datasetLen):
            data = []
            for device in TriggerDeviceList:
                if device == targetDevice:
                    continue
                data.append(random.randint(-1, deviceStateDict[device]))
            for j in range(deviceStateDict[targetDevice]+1):
                data2 = data.copy()
                data2.append(j-1)
                MLdataset.append(data2)

        with open(modelPath + "DT_A.pkl", 'rb') as f:
            dt_A = pickle.load(f)
        dtLabel = dt_A.predict(MLdataset)
        with open(modelPath + "RF_A.pkl", 'rb') as f:
            rf_A = pickle.load(f)
        rfLabel = rf_A.predict(MLdataset)
        with open(modelPath + "ADA_A.pkl", 'rb') as f:
            ad_A = pickle.load(f)
        adaLabel = ad_A.predict(MLdataset)
        with open(modelPath + "MLP_A.pkl", 'rb') as f:
            mlp_A = pickle.load(f)
        mlpLabel = mlp_A.predict(MLdataset)

        MLdataset = np.array(MLdataset)

        targetLabel = list(MLdataset.T[-1])
        MLdataset = np.delete(MLdataset, len(TriggerDeviceList) - 1, axis=1)
        dtDataset = np.insert(MLdataset, MLdataset.shape[1], dtLabel, axis=1)
        rfDataset = np.insert(MLdataset, MLdataset.shape[1], rfLabel, axis=1)
        adaDataset = np.insert(MLdataset, MLdataset.shape[1], adaLabel, axis=1)
        mlpDataset = np.insert(MLdataset, MLdataset.shape[1], mlpLabel, axis=1)

        npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            dataset = pickle.load(f)
        dataset = np.array(dataset)
        y = dataset[1:, targetDeviceNum].copy().astype(np.float64)
        X = np.delete(dataset[1:], targetDeviceNum, axis=1).astype(np.float64)
        X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.2, random_state=0)

        X_train, X_test, y_train, y_test = train_test_split(dtDataset, targetLabel, test_size=0.2, random_state=0)
        dt = tree.DecisionTreeClassifier(splitter='best')
        dt.fit(X_train, y_train)
        score = dt.score(X_test1, y_test1)
        logging.critical("DT Attack score: " + str(score))
        if score > localScoreList[0]:
            localScoreList[0] = score

        X_train, X_test, y_train, y_test = train_test_split(rfDataset, targetLabel, test_size=0.2, random_state=0)
        rf = ensemble.RandomForestClassifier(n_estimators=10)
        rf.fit(X_train, y_train)
        score = rf.score(X_test1, y_test1)
        logging.critical("RF Attack score: " + str(score))
        if score > localScoreList[1]:
            localScoreList[1] = score

        X_train, X_test, y_train, y_test = train_test_split(adaDataset, targetLabel, test_size=0.2, random_state=0)
        ada = ensemble.AdaBoostClassifier(n_estimators=10)
        ada.fit(X_train, y_train)
        score = ada.score(X_test1, y_test1)
        logging.critical("ADA Attack score: " + str(score))
        if score > localScoreList[2]:
            localScoreList[2] = score

        X_train, X_test, y_train, y_test = train_test_split(mlpDataset, targetLabel, test_size=0.2, random_state=0)
        mlp = neural_network.MLPClassifier(max_iter=300)
        mlp.fit(X_train, y_train)
        score = mlp.score(X_test1, y_test1)
        logging.critical("MLP Attack score: " + str(score))
        if score > localScoreList[3]:
            localScoreList[3] = score
        logging.critical('——————————————————————————')

    logging.critical('DT BEST Attack score: ' + str(localScoreList[0]))
    logging.critical('RF BEST Attack score: ' + str(localScoreList[1]))
    logging.critical('ADA BEST Attack score: ' + str(localScoreList[2]))
    logging.critical('MLP BEST Attack score: ' + str(localScoreList[3]))
    for i in range(len(scoreList)):
        scoreList[i] += localScoreList[i]
    logging.critical(
        '——————————————————————————————————————————————————————————————————————————————————————————————')


def AttackStatesWithTarget(runNum, datasetLen, scoreList, kdn, targetList):
    logging.critical('ML Attack States runNum: %d', runNum)
    modelPath = "Model" + os.sep + str(runNum) + os.sep
    npyPath = "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    TriggerDeviceList = np.load(npyPath + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    attackTargetList = {}
    for device in TriggerDeviceList:
        attackTargetList[device] = 0
    for strrule in targetList:
        #print(strrule)
        strlist = strrule.split('&')
        for rule in strlist:
            rule = rule.replace('>', '<').replace(' ', '')
            device = rule.split('<')[0]
            attackTargetList[device] += 1
    MLLabel = np.load(npyPath + 'MLLabel.npy', allow_pickle=True).tolist()
    deviceObjDict = np.load(npyPath + 'deviceObjDict.npy', allow_pickle=True).item()
    deviceStateDict = {}
    for device in TriggerDeviceList:
        deviceStateDict[device] = deviceObjDict[device].getStateNum()
    logging.critical('——————————————————————————')
    localScoreList = [0 for i in range(len(scoreList))]
    attackCount=0
    for targetDeviceNum in range(0, len(TriggerDeviceList)):
        MLdataset = []
        targetDevice = TriggerDeviceList[targetDeviceNum]
        if attackTargetList[targetDevice] == 0:
            continue
        attackCount += 1
        logging.critical('targetDevice: %s', targetDevice)
        for i in range(datasetLen):
            data = []
            for device in TriggerDeviceList:
                if device == targetDevice:
                    data.append(-2)
                    continue
                data.append(random.randint(-1, deviceStateDict[device]))
            for j in range(deviceStateDict[targetDevice]+1):
                data2 = data.copy()
                data2[targetDeviceNum] = j
                MLdataset.append(data2)

        with open(modelPath + "DT_A.pkl", 'rb') as f:
            dt_A = pickle.load(f)
        dtLabel = dt_A.predict(MLdataset)
        with open(modelPath + "RF_A.pkl", 'rb') as f:
            rf_A = pickle.load(f)
        rfLabel = rf_A.predict(MLdataset)
        with open(modelPath + "ADA_A.pkl", 'rb') as f:
            ad_A = pickle.load(f)
        adaLabel = ad_A.predict(MLdataset)
        with open(modelPath + "MLP_A.pkl", 'rb') as f:
            mlp_A = pickle.load(f)
        mlpLabel = mlp_A.predict(MLdataset)

        MLdataset = np.array(MLdataset)

        targetLabel = list(MLdataset.T[-1])
        MLdataset = np.delete(MLdataset, len(TriggerDeviceList) - 1, axis=1)
        dtDataset = np.insert(MLdataset, MLdataset.shape[1], dtLabel, axis=1)
        rfDataset = np.insert(MLdataset, MLdataset.shape[1], rfLabel, axis=1)
        adaDataset = np.insert(MLdataset, MLdataset.shape[1], adaLabel, axis=1)
        mlpDataset = np.insert(MLdataset, MLdataset.shape[1], mlpLabel, axis=1)

        npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            dataset = pickle.load(f)
        dataset = np.array(dataset)
        y = dataset[1:, targetDeviceNum].copy().astype(np.float64)
        X = np.delete(dataset[1:], targetDeviceNum, axis=1).astype(np.float64)
        X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.2, random_state=0)

        X_train, X_test, y_train, y_test = train_test_split(dtDataset, targetLabel, test_size=0.2, random_state=0)
        dt = tree.DecisionTreeClassifier(splitter='best')
        dt.fit(X_train, y_train)
        class_labels = np.unique(y_test1)
        score = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, dt.predict_proba(X_test1)[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count-=1
            count+=1
            score += auc
            logging.critical('dt Class %d ROC AUC: %f', class_labels[i], auc)
        score /=  count
        logging.critical("DT Attack score: " + str(score))
        localScoreList[0] += score

        X_train, X_test, y_train, y_test = train_test_split(rfDataset, targetLabel, test_size=0.2, random_state=0)
        rf = ensemble.RandomForestClassifier(n_estimators=10)
        rf.fit(X_train, y_train)
        score = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, rf.predict_proba(X_test1)[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count-=1
            count+=1
            logging.critical('rf Class %d ROC AUC: %f', class_labels[i], auc)
            score += auc
        score /= count
        logging.critical("RF Attack score: " + str(score))
        localScoreList[1] += score

        X_train, X_test, y_train, y_test = train_test_split(adaDataset, targetLabel, test_size=0.2, random_state=0)
        ada = ensemble.AdaBoostClassifier(n_estimators=10)
        ada.fit(X_train, y_train)
        score = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, ada.predict_proba(X_test1)[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count -= 1
            count += 1
            score += auc
            logging.critical('ada Class %d ROC AUC: %f', class_labels[i], auc)
        score /= count
        logging.critical("ADA Attack score: " + str(score))
        localScoreList[2] += score

        # X_train, X_test, y_train, y_test = train_test_split(mlpDataset, targetLabel, test_size=0.2, random_state=0)
        # mlp = neural_network.MLPClassifier(max_iter=300)
        # mlp.fit(X_train, y_train)
        # fpr, tpr, thresholds = metrics.roc_curve(y_test1, mlp.predict(X_test1), pos_label=2)
        # score = metrics.auc(fpr, tpr)
        # logging.critical("MLP Attack score: " + str(score))
        # localScoreList[3] += score
        #
        # p = 1/(deviceStateDict[targetDevice]+1)
        # r = p
        # localScoreList[4] += 2*p*r/(p+r)
        # logging.critical("RandomGuess Attack score: " + str(2*p*r/(p+r)))
        logging.critical('——————————————————————————')
    if attackCount != 0:
        for i in range(len(localScoreList)):
            localScoreList[i] /= attackCount
        logging.critical('DT Average Attack score: ' + str(localScoreList[0]))
        logging.critical('RF Average Attack score: ' + str(localScoreList[1]))
        logging.critical('ADA Average Attack score: ' + str(localScoreList[2]))
        logging.critical('MLP Average Attack score: ' + str(localScoreList[3]))
        logging.critical('RandomGuess Average Attack score: ' + str(localScoreList[4]))
    else:
        logging.critical('Attack Failed ' + str(localScoreList[0]))
    for i in range(len(scoreList)):
        scoreList[i] += localScoreList[i]
    logging.critical(
        '——————————————————————————————————————————————————————————————————————————————————————————————')


def AttackStatesV2(runNum, datasetLen, scoreList, kdn):
    logging.critical('ML Attack States runNum: %d', runNum)
    modelPath = "Model" + os.sep + str(runNum) + os.sep
    npyPath = "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    TriggerDeviceList = np.load(npyPath + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    MLLabel = np.load(npyPath + 'MLLabel.npy', allow_pickle=True).tolist()
    deviceObjDict = np.load(npyPath + 'deviceObjDict.npy', allow_pickle=True).item()
    deviceStateDict = {}
    for device in TriggerDeviceList:
        deviceStateDict[device] = deviceObjDict[device].getStateNum()
    logging.critical('——————————————————————————')
    localScoreList = [0 for i in range(len(scoreList))]
    for targetDeviceNum in range(kdn, len(TriggerDeviceList)):
        MLdataset = []
        targetDevice = TriggerDeviceList[targetDeviceNum]
        logging.critical('targetDevice: %s', targetDevice)
        for i in range(datasetLen):
            data = []
            for device in TriggerDeviceList:
                if device == targetDevice:
                    continue
                data.append(random.randint(-1, deviceStateDict[device]))
            for j in range(deviceStateDict[targetDevice]+1):
                data2 = data.copy()
                data2.append(j-1)
                MLdataset.append(data2)
        MLdataset = np.array(MLdataset)
        target=MLdataset[:,-1]
        MLdataset=np.delete(MLdataset,-1,axis=1)
        MLdataset = np.insert(MLdataset, targetDeviceNum, target, axis=1)
        with open(modelPath + "DT.pkl", 'rb') as f:
            dt_A = pickle.load(f)
        dtLabel = dt_A.predict(MLdataset)
        with open(modelPath + "RF.pkl", 'rb') as f:
            rf_A = pickle.load(f)
        rfLabel = rf_A.predict(MLdataset)
        with open(modelPath + "ADA.pkl", 'rb') as f:
            ad_A = pickle.load(f)
        adaLabel = ad_A.predict(MLdataset)

        MLdataset = np.array(MLdataset)

        targetLabel = list(MLdataset.T[-1])
        MLdataset = np.delete(MLdataset, len(TriggerDeviceList) - 1, axis=1)
        dtDataset = np.insert(MLdataset, MLdataset.shape[1], dtLabel, axis=1)
        rfDataset = np.insert(MLdataset, MLdataset.shape[1], rfLabel, axis=1)
        adaDataset = np.insert(MLdataset, MLdataset.shape[1], adaLabel, axis=1)

        npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            dataset = pickle.load(f)
        dataset = np.array(dataset)
        y = dataset[1:, targetDeviceNum].copy().astype(np.float64)
        X = np.delete(dataset[1:], targetDeviceNum, axis=1).astype(np.float64)
        X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.2, random_state=0)

        X_train, X_test, y_train, y_test = train_test_split(dtDataset, targetLabel, test_size=0.2, random_state=0)
        dt = tree.DecisionTreeClassifier(splitter='best')
        dt.fit(X_train, y_train)
        score = dt.score(X_test1, y_test1)
        logging.critical("DT Attack score: " + str(score))
        if score > localScoreList[0]:
            localScoreList[0] = score

        X_train, X_test, y_train, y_test = train_test_split(rfDataset, targetLabel, test_size=0.2, random_state=0)
        rf = ensemble.RandomForestClassifier(n_estimators=10)
        rf.fit(X_train, y_train)
        score = rf.score(X_test1, y_test1)
        logging.critical("RF Attack score: " + str(score))
        if score > localScoreList[1]:
            localScoreList[1] = score

        X_train, X_test, y_train, y_test = train_test_split(adaDataset, targetLabel, test_size=0.2, random_state=0)
        ada = ensemble.AdaBoostClassifier(n_estimators=10)
        ada.fit(X_train, y_train)
        score = ada.score(X_test1, y_test1)
        logging.critical("ADA Attack score: " + str(score))
        if score > localScoreList[2]:
            localScoreList[2] = score

        logging.critical('——————————————————————————')

    logging.critical('DT BEST Attack score: ' + str(localScoreList[0]))
    logging.critical('RF BEST Attack score: ' + str(localScoreList[1]))
    logging.critical('ADA BEST Attack score: ' + str(localScoreList[2]))
    for i in range(len(scoreList)):
        scoreList[i] += localScoreList[i]
    logging.critical(
        '——————————————————————————————————————————————————————————————————————————————————————————————')


if __name__ == '__main__':
    scoreList_S = [0 for i in range(4)]
    AttackStatesV2(0, 10000, scoreList_S,10)
