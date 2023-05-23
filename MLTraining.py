import math
import random

from allClass import *
import numpy as np
from sklearn import *
from sklearn.metrics import classification_report
from sklearn.tree import export_text, _tree


def DT(X_train, y_train, X_test, y_test):
    clf = tree.DecisionTreeClassifier(splitter='best')
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # report = classification_report(y_test, clf.predict(X_test))
    # print(report)
    # tree.plot_tree(clf)
    return score, clf


def RF(X_train, y_train, X_test, y_test):
    clf = ensemble.RandomForestClassifier(n_estimators=10)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # report = classification_report(y_test, clf.predict(X_test))
    # print(report)
    return score, clf


def ADA(X_train, y_train, X_test, y_test):
    clf = ensemble.AdaBoostClassifier(n_estimators=10)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # report = classification_report(y_test, clf.predict(X_test))
    # print(report)
    return score, clf


def LI(X_train, y_train, X_test, y_test):
    clf = linear_model.LinearRegression()
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    return score, clf


def LR(X_train, y_train, X_test, y_test):
    clf = linear_model.LogisticRegression()
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # report = classification_report(y_test, clf.predict(X_test))
    # print(report)
    return score, clf


def MLP(X_train, y_train, X_test, y_test):
    clf = neural_network.MLPClassifier(max_iter=300)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # report = classification_report(y_test, clf.predict(X_test))
    # print(report)
    return score, clf


def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    pathto = dict()

    global k
    k = 0
    outputList = []

    def recurse(node, depth, parent, output=outputList):
        global k
        indent = "  " * depth

        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            s = "{} <= {} ".format(name, threshold, node)
            if node == 0:
                pathto[node] = s
            else:
                pathto[node] = pathto[parent] + ' & ' + s

            recurse(tree_.children_left[node], depth + 1, node)
            s = "{} > {}".format(name, threshold)
            if node == 0:
                pathto[node] = s
            else:
                pathto[node] = pathto[parent] + ' & ' + s
            recurse(tree_.children_right[node], depth + 1, node)
        else:
            k = k + 1
            # print(k, ')', pathto[parent], np.argmax(tree_.value[node])-1)
            if parent != 0:
                output.append(pathto[parent])

    recurse(0, 1, 0, outputList)
    return outputList


def ML(runNum, scoreList, scoreList_A):
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('ML Model Train runNum: %d', runNum)
    TriggerDeviceList = np.load(currentDir() + os.sep + "Environment" + os.sep + str(
        runNum) + os.sep + "npy" + os.sep + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    # load data
    X_train, y_train, X_test, y_test = datasetLoad(runNum, 0, 0.2)
    X_train_A, y_train_A, axt, ayt = datasetLoad(runNum, 1, 0.2)
    # data type
    X_train = X_train.astype(np.float64)
    X_test = X_test.astype(np.float64)
    y_train = y_train.astype(np.float64)
    y_test = y_test.astype(np.float64)
    X_train_A = X_train_A.astype(np.float64)
    y_train_A = y_train_A.astype(np.float64)
    logging.critical('——————————————————————————————————————')

    # DT model 决策树模型
    score, dt = DT(X_train, y_train, X_test, y_test)
    score_A, dt_A = DT(X_train_A, y_train_A, X_test, y_test)
    logging.critical('DT Score: %f', score)
    logging.critical('DT Attack Score: %f', score_A)
    logging.critical('——————————————————————————————————————')
    writeAttackModel(dt, 'DT', runNum)
    writeAttackModel(dt_A, 'DT_A', runNum)
    dt_target = tree_to_code(dt_A, TriggerDeviceList)

    scoreList[0] += score
    scoreList_A[0] += score_A

    # RF model 随机森林模型
    score, rf = RF(X_train, y_train, X_test, y_test)
    score_A, rf_A = RF(X_train_A, y_train_A, X_test, y_test)
    logging.critical('RF Score: %f', score)
    logging.critical('RF Attack Score: %f', score_A)
    logging.critical('——————————————————————————————————————')
    writeAttackModel(rf, 'RF', runNum)
    writeAttackModel(rf_A, 'RF_A', runNum)
    scoreList[1] += score
    scoreList_A[1] += score_A

    # AdaBoost model
    score, ad = ADA(X_train, y_train, X_test, y_test)
    score_A, ad_A = ADA(X_train_A, y_train_A, X_test, y_test)
    logging.critical('ADA Score: %f', score)
    logging.critical('ADA Attack Score: %f', score_A)
    logging.critical('——————————————————————————————————————')
    writeAttackModel(ad, 'ADA', runNum)
    writeAttackModel(ad_A, 'ADA_A', runNum)
    scoreList[2] += score
    scoreList_A[2] += score_A

    # # Linear Regression model 线性回归模型
    # score, li = LI(X_train, y_train, X_test, y_test)
    # score_A, li_A = LI(X_train_A, y_train_A, X_test, y_test)
    # logging.critical('LI Score: %f', score)
    # logging.critical('LI Attack Score: %f', score_A)
    # writeAttackModel(li, 'LI', runNum)
    # writeAttackModel(li_A, 'LI_A', runNum)
    # scoreList[3] += score
    # scoreList_A[3] += score_A
    #
    # # LR model 逻辑回归模型
    # score, lr = LR(X_train, y_train, X_test, y_test)
    # score_A, lr_A = LR(X_train_A, y_train_A, X_test, y_test)
    # logging.critical('LR Score: %f', score)
    # logging.critical('LR Attack Score: %f', score_A)
    # writeAttackModel(lr, 'LR', runNum)
    # writeAttackModel(lr_A, 'LR_A', runNum)
    # scoreList[4] += score
    # scoreList_A[4] += score_A

    # MLP model 多层感知机模型
    score, mlp = MLP(X_train, y_train, X_test, y_test)
    score_A, mlp_A = MLP(X_train_A, y_train_A, X_test, y_test)
    logging.critical('MLP Score: %f', score)
    logging.critical('MLP Attack Score: %f', score_A)
    writeAttackModel(mlp, 'MLP', runNum)
    writeAttackModel(mlp_A, 'MLP_A', runNum)
    scoreList[3] += score
    scoreList_A[3] += score_A

    return dt_target


def MLV2(runNum, scoreList, kdn):
    logging.critical('——————————————————————————————————————————————————————————————————————————————————————————————')
    logging.critical('ML Model Train runNum: %d', runNum)

    npyfilepath = currentDir() + os.sep + "Environment" + os.sep + str(runNum) + os.sep + "npy" + os.sep
    TriggerDeviceList = np.load(currentDir() + os.sep + "Environment" + os.sep + str(
        runNum) + os.sep + "npy" + os.sep + 'TriggerDeviceList.npy', allow_pickle=True).tolist()
    knowDeviceList = np.load(npyfilepath + 'knowDevicesList.npy', allow_pickle=True).tolist()
    MLLabel = np.load(npyfilepath + 'MLLabel.npy', allow_pickle=True).tolist()
    deviceObjDict = np.load(npyfilepath + 'deviceObjDict.npy', allow_pickle=True).item()
    labelNum = 0
    datasetLen=10000

    for i in range(len(knowDeviceList)):
        if knowDeviceList[i] == MLLabel:
            labelNum = i
    TriggerDeviceList.insert(i,MLLabel[0])
    # load data
    data = datasetLoadV2(runNum, 1, 0.2)
    label = data[1:, -1]
    data = data[:, :-1]
    kx = data[1:, 0:kdn - 1]
    ukx = data[1:, kdn - 1:]
    kx = np.insert(kx, labelNum, label, axis=1)
    dtList = []
    rfList = []
    adList = []
    for i in range(kdn):
        newlabel = kx[:, i]
        kx2 = np.delete(kx, i, axis=1)
        X = np.concatenate((kx2, ukx), axis=1)
        y = newlabel
        # split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

        # data type
        X_train = X_train.astype(np.float64)
        X_test = X_test.astype(np.float64)
        y_train = y_train.astype(np.float64)
        y_test = y_test.astype(np.float64)
        logging.critical('——————————————————————————————————————')

        # DT model 决策树模型
        score, dt = DT(X_train, y_train, X_test, y_test)
        logging.critical('DT Score: %f', score)
        logging.critical('——————————————————————————————————————')
        dtList.append(dt)


        # RF model 随机森林模型
        score, rf = RF(X_train, y_train, X_test, y_test)
        logging.critical('RF Score: %f', score)
        logging.critical('——————————————————————————————————————')
        rfList.append(rf)

        # AdaBoost model
        score, ad = ADA(X_train, y_train, X_test, y_test)
        logging.critical('ADA Score: %f', score)
        logging.critical('——————————————————————————————————————')
        adList.append(ad)

    deviceStateDict = {}
    for device in TriggerDeviceList:
        deviceStateDict[device] = deviceObjDict[device].getStateNum()
    for targetDeviceNum in range(kdn,len(TriggerDeviceList)):
        MLdataset = []
        targetDevice = TriggerDeviceList[targetDeviceNum]
        logging.critical('targetDevice: %s', targetDevice)
        for i in range(datasetLen):
            data = []
            for device in TriggerDeviceList:
                if device == targetDevice:
                    continue
                data.append(random.randint(0, deviceStateDict[device]))
            for j in range(deviceStateDict[targetDevice] + 1):
                data2 = data.copy()
                data2.append(j - 1)
                MLdataset.append(data2)
        MLdataset = np.array(MLdataset)
        target = MLdataset[:, -1]
        MLdataset = np.delete(MLdataset, -1, axis=1)
        MLdataset = np.insert(MLdataset, targetDeviceNum, target, axis=1)
        dtList2 = []
        rfList2 = []
        adList2 = []
        for i in range(kdn):
            X = np.delete(MLdataset, i, axis=1)
            # data type
            X = X.astype(np.float64)
            # DT model 决策树模型
            dt = dtList[i]
            dty = dt.predict(X)

            # RF model 随机森林模型
            rf = rfList[i]
            rfy = rf.predict(X)

            # AdaBoost model
            ad = adList[i]
            ady = ad.predict(X)

            dtX = np.insert(X, i, dty, axis=1)
            dtt = dtX[:, targetDeviceNum]
            dtX = np.delete(dtX, targetDeviceNum, axis=1)
            dt2 = tree.DecisionTreeClassifier(splitter='best')
            dt2.fit(dtX, dtt)
            dtList2.append(dt2)

            rfX = np.insert(X, i, rfy, axis=1)
            rft = rfX[:, targetDeviceNum]
            rfX = np.delete(rfX, targetDeviceNum, axis=1)
            rf2 = ensemble.RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
            rf2.fit(rfX, rft)
            rfList2.append(rf2)

            adX = np.insert(X, i, ady, axis=1)
            adt = adX[:, targetDeviceNum]
            adX = np.delete(adX, targetDeviceNum, axis=1)
            ad2 = ensemble.AdaBoostClassifier(n_estimators=100, random_state=0)
            ad2.fit(adX, adt)
            adList2.append(ad2)

        # test
        with open(npyfilepath + 'MLDataset.pkl', 'rb') as f:
            dataset = pickle.load(f)
        dataset = np.array(dataset)
        y = dataset[1:, targetDeviceNum].copy().astype(np.float64)
        X = np.delete(dataset[1:], targetDeviceNum, axis=1).astype(np.float64)
        X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.2, random_state=0)
        dtans = np.zeros_like(dtList2[0].predict_proba(X_test1))
        rfans = np.zeros_like(rfList2[0].predict_proba(X_test1))
        adans = np.zeros_like(adList2[0].predict_proba(X_test1))
        for i in range(kdn):
            dt2 = dtList2[i]
            rf2 = rfList2[i]
            ad2 = adList2[i]
            dtans += dt2.predict_proba(X_test1)
            rfans += rf2.predict_proba(X_test1)
            adans += ad2.predict_proba(X_test1)

        dtans /= kdn
        rfans /= kdn
        adans /= kdn

        class_labels = np.unique(y_test1)  # 获取所有类别的标签值
        dtauc = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, dtans[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count -= 1
            count += 1
            dtauc += auc
            logging.critical('dt Class %d ROC AUC: %f', class_labels[i], auc)
        dtauc /= count
        logging.critical('dt AUC: %f', dtauc)
        scoreList[0]+=dtauc

        rfauc = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, rfans[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count -= 1
            count += 1
            rfauc += auc
            logging.critical('rf Class %d ROC AUC: %f', class_labels[i], auc)
        rfauc /= count
        logging.critical('rf AUC: %f', rfauc)
        scoreList[1]+=rfauc

        adauc = 0
        count = 0
        for i in range(len(class_labels)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test1, adans[:,1], pos_label=i)
            auc = metrics.auc(fpr, tpr)
            if math.isnan(auc):
                auc = 0
                count -= 1
            count += 1
            adauc += auc
            logging.critical('ada Class %d ROC AUC: %f', class_labels[i], auc)
        adauc /= count
        logging.critical('ad AUC: %f', adauc)
        scoreList[2]+=adauc









if __name__ == '__main__':
    modelNum = 4
    runNum = 100
    scoreList = [0 for i in range(modelNum)]
    scoreList_A = [0 for i in range(modelNum)]
    alltargetlist = []
    for i in range(runNum):
        MLV2(i, scoreList, scoreList_A, kdn=10)
    for i in range(modelNum):
        scoreList[i] /= runNum
        scoreList_A[i] /= runNum
    logging.critical('——————————————————————————————————————')
    for i in range(modelNum):
        logging.critical('model:' + str(modelNum) + ' finalScore: %f', scoreList[i])
        logging.critical('model:' + str(modelNum) + ' finalScore_A: %f', scoreList_A[i])
