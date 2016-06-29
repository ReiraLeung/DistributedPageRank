# -*- coding: utf-8 -*-
import init
import sys
import os, json
import snap

error = 0
config_file = open('../config.txt')
global GlobalInfo
GlobalInfo = {}
try:
    GlobalInfo = json.loads( config_file.read( ))
except:
    print('Config File Error!')
    error = 1
finally:
    config_file.close( )
    if (error == 1):
        sys.exit()

print (GlobalInfo['worker-num'])
#C= [NodeFile, DataFile, index, NodeinCount, NodeRankFile, DataSet]
C = init.command()
print (C)

ntTable = {}
nodeInfo = {}
if not (os.path.exists(C[0]) and os.path.exists(C[3]) and os.path.exists(C[4])):
    N = init.createNode(C[0],C[1],C[2],GlobalInfo['worker-num'])
    print(N[2])
    ntTable = N[0]

    f = open(C[3],'w')
    for key in ntTable:
        nodeInfo[key] = (N[1][key], 0.15)
        f.write(str(key)+" "+str(N[1][key])+"\n")
    f.close()
    if not os.path.exists(C[4]): #如果NodeRankFile是不存在的，我们必须用0.15来初始化
        f = open(C[4],'w')
        i=0
        while i<=N[2]:
            if i % 3 == C[2]:
                f.write(str(i)+" 0.15\n")
            i += 1
        f.close()
else:
    ntTable = init.readNode(C[0])
    nodeInfo = init.readNodeinCount(C[3])
    nodeInfo = init.readNodeRank(C[4],nodeInfo)


print(str(ntTable))
print(str(nodeInfo))
snapFile = snapFile = '../data/'+C[5]+'_'+str(C[2])+'.snap'
if os.path.exists(snapFile):
    recInfo = snap.recoverNodeInfo(C[5], C[2])
    print(recInfo)
snap.snapshot(nodeInfo,C[5],C[2])

GlobalInfo['superstep'] = 0
GlobalInfo['finish'] = 0
GlobalInfo['success'] = 0
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host= GlobalInfo['host']))
channel = connection.channel()
channel.queue_declare(queue='master', durable=True)
for i in range(0, GlobalInfo['worker-num']):
    channel.queue_declare(queue='worker-%d' % i, durable=True)
    GlobalInfo[i] = 1
    
channel.basic_consume(callback,
                queue='worker-%d' % i,)
