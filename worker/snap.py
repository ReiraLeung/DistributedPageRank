#coding:utf-8

import sys
import os

def snapshotMessage(temprank,DataSet,worker_index,GlobalInfo):
    msnapFile = '../data/'+DataSet+'_'+str(worker_index)+'.msnap'
    f = open(msnapFile,'w')
    f.write(GlobalInfo['host']+'\n')
    f.write(str(GlobalInfo['total_iteration'])+'\n')
    f.write(str(GlobalInfo['finish'])+'\n')
    f.write(str(GlobalInfo['worker-num'])+'\n')
    f.write(str(GlobalInfo['superstep'])+'\n')
    for i in range(0, GlobalInfo['worker-num']):
        f.write(str(GlobalInfo[i])+'\n')
    for key in temprank.keys():
        f.write("%d %.17f\n" % (key, temprank[key]))
    f.close()

def snapshotSuperstep(nodeInfo,DataSet,worker_index):
    ssnapFile = '../data/'+DataSet+'_'+str(worker_index)+'.ssnap'
    f = open(ssnapFile, 'w')
    for key in nodeInfo.keys():
        f.write("%d %.17f\n" % (key, nodeInfo[key][1]))
    f.close()


def recoverState(DataSet,worker_index,GlobalInfo, nodeInfo, temprank):
    msnapFile = '../data/'+DataSet+'_'+str(worker_index)+'.msnap'
    ssnapFile = '../data/'+DataSet+'_'+str(worker_index)+'.ssnap'
    NodeinFile = '../data/'+DataSet+'_count_'+str(worker_index)+'.txt'
    f =  open(NodeinFile, 'r')
    msnap = open(msnapFile, 'r')
    ssnap = open(ssnapFile, 'r')
    i = 0
    for line in f:
        split_line = line.split(' ', 1)
        node = int(split_line[0])
        nodein = int(split_line[1])
        nodeInfo[node] = (nodein, 0)
    for rank in ssnap:
        split_rank = rank.split(' ', 1)
        node = int(split_rank[0])
        nrank = float(split_rank[1])
        nodeInfo[node] = (nodeInfo[node][0], nrank)
    snap = msnap.readlines()
    GlobalInfo['host'] = snap[0].strip('\n')
    GlobalInfo['total_iteration'] = int(snap[1])
    GlobalInfo['finish'] = int(snap[2])
    GlobalInfo['worker-num'] = int(snap[3])
    GlobalInfo['superstep'] = int(snap[4])
    for i in range(0, GlobalInfo['worker-num']):
        GlobalInfo[i] = int(snap[i+5])
    for k in range(i+6, len(snap)):
        split_rank = snap[k].split(' ', 1)
        node = int(split_rank[0])
        nrank = float(split_rank[1])
        temprank[node] = nrank
    
def finalChange(DataSet, worker_index):
    oldID = '../data/'+DataSet+'_'+str(worker_index)+'.ssnap'
    msnap = '../data/'+DataSet+'_'+str(worker_index)+'.msnap'
    newID = '../data/'+DataSet+'_rank_'+str(worker_index)+'.txt'
    if os.path.exists(newID):
        os.remove(newID)
    os.rename(oldID, newID)
    os.remove(msnap)