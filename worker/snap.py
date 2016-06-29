#coding:utf-8

import sys
import os

def snapshot(nodeInfo,DataSet,worker_index):
    snapFile = '../data/'+DataSet+'_'+str(worker_index)+'.snap'
    f = open(snapFile,'w')
    for key in nodeInfo.keys():
        f.write("%d %f\n" % (key, nodeInfo[key][1]))
    f.close()

def snap_swap(DataSet,worker_index):
    oldID = '../data/'+DataSet+'_'+str(worker_index)+'.snap'
    newID = '../data/'+DataSet+'_rank_'+str(worker_index)+'.txt'
    if os.path.exists(newID):
        os.remove(newID)
    os.rename(oldID, newID)

def recoverNodeInfo(DataSet,worker_index):
    snapFile = '../data/'+DataSet+'_'+str(worker_index)+'.snap'
    NodeinFile = '../data/'+DataSet+'_count_'+str(worker_index)+'.txt'
    f =  open(NodeinFile, 'r')
    snap = open(snapFile, 'r')
    infoList = {}
    for line in f:
        split_line = line.split(' ', 1)
        node = int(split_line[0])
        nodein = int(split_line[1])
        infoList[node] = (nodein, 0)
    for rank in snap:
        split_rank = rank.split(' ', 1)
        node = int(split_rank[0])
        nrank = float(split_rank[1])
        infoList[node] = (infoList[node][0], nrank)
    return infoList