# -*- coding: utf-8 -*-
import init
import sys
import pika
import os, json
import snap

def resetInfo():
	global GlobalInfo
	for i in range(0, GlobalInfo['worker-num']):
		GlobalInfo[i] = 1
	GlobalInfo['finish'] = 0



def countSendPackages(channel):
	global GlobalInfo
	global nodeInfo
	global ntTable
	global this_index
	messages = []
	for i in range(0, GlobalInfo['worker-num']):
		newResult = {
			'from' : this_index,
			'instruction' : 'count',
			'superstep' : GlobalInfo['superstep'],
			'rank' : {}
			}
		messages.append(newResult)
	for node in ntTable:
		nodelist = ntTable[node]
		rank = nodeInfo[node][1]
		total = len(nodelist)
		sendrank = rank/total
		for toNodestr in nodelist:
			toNode  = int(toNodestr)
			worker_id = toNode % GlobalInfo['worker-num']
			rankDict = messages[worker_id]['rank']
			if toNode in rankDict:
				rankDict[toNode] = rankDict[toNode] + sendrank
			else:
				rankDict[toNode] = sendrank
	
	for i in range(0, GlobalInfo['worker-num']):
		if i == this_index:
			if GlobalInfo[i] == 1:
				ranks = messages[i]['rank']
				getRankFromMessage(ranks)
				GlobalInfo['finish'] += 1 # this is from worker-i itself
				GlobalInfo[i] = 0
		else:
			#print (str(json.dumps(messages[i])))
			channel.basic_publish(exchange='',
				routing_key='worker-%d' % i,
				body=json.dumps(messages[i]),
				properties=pika.BasicProperties(
				delivery_mode = 2, # make message persistent
				))
			print("[*] worker-%d Sent to %d in round %d"%(this_index,i,GlobalInfo['superstep']))



def getRankFromMessage(ranks):
	global temprank
	for node in ranks:
		temprank[int(node)] += ranks[node]

def temp2dict():
	global temprank
	global nodeInfo
	for node in temprank:
		nodeInfo[node] =(nodeInfo[node][0], temprank[node])
		temprank[node] = 0.15  #everytime temprank is start from 0.15, not only the first time

def final_temp2dict():
	global temprank
	global nodeInfo
	for node in temprank:
		nodeInfo[node] =(nodeInfo[node][0], temprank[node])

def callback(ch, method, properties, body):
	global GlobalInfo
	global this_index
	global temprank
	global DataSet
	message = json.loads(str(body)[2:-1])
	print("[+] worker-%d: Received message from %r" %(this_index, message['from']))
	if (message['from'] == 'master'):
		# if message['superstep'] == 3:
		# 	print('test recover, so exit')
		# 	sys.exit()
		if(message['instruction'] == 'success'):# finish signal from master
			print("worker-%d: master ask me to exit, Byebye~"%this_index)
			ch.basic_ack(delivery_tag = method.delivery_tag)
			sys.exit()
		else: # start next superstep signal form master
			if(message['superstep'] > GlobalInfo['superstep']): #if not start, then start
				print("worker-%d: master arrive first in this superstep %d counting starts."%(this_index,message['superstep']))
				GlobalInfo['superstep'] = message['superstep']
				resetInfo()
				countSendPackages(channel)
			else:
				print("worker-%d: master arrive later, counting is already started, but this is OK."%this_index)
			ch.basic_ack(delivery_tag = method.delivery_tag)
	else:
		fromID = message['from']
		print ('message superstep: %d' % message['superstep'])
		print ('local superstep: %d' % GlobalInfo['superstep'])
		print ('GlobalInfo[fromID]: %d' % GlobalInfo[fromID])
		if GlobalInfo[fromID] == 1:
			if(message['superstep'] > GlobalInfo['superstep']): #if not start, then start
				print("worker-%d: worker-%d arrives first in this superstep %d, counting starts."%(this_index,fromID,message['superstep']))
				GlobalInfo['superstep'] = message['superstep']
				resetInfo()
				countSendPackages(channel)
				getRankFromMessage(message['rank'])
				GlobalInfo['finish'] += GlobalInfo[fromID]
			else:
				print("worker-%d: worker-%d arrives in this superstep %d, add this to counting."%(this_index,fromID,message['superstep']))
				getRankFromMessage(message['rank'])
				GlobalInfo['finish'] += GlobalInfo[fromID]
			
			GlobalInfo[fromID] = 0 #this message is readalready in thie superstep, set it to 0
			print("worker-%d: message of worker-%d has been handled in this superstep %d."%(this_index,fromID,message['superstep']))
			if GlobalInfo['finish']==GlobalInfo['worker-num']: #if worker-i received all messages in one superstep
				print('worker-%d: worker handled all messages in superstep: %d' % (this_index, GlobalInfo['superstep']))
				if(GlobalInfo['superstep'] < GlobalInfo['total_iteration']):
					signal = 'finish'
					temp2dict() # copy the temp counting result to middle dictionary nodeInfo, but not the file!
					###############################
					#!!!!here store the nodeInfo in snap file!!!!
					################################
					snap.snapshot(nodeInfo, DataSet, this_index)
					################################
				else:
					signal = 'success'
					final_temp2dict()
					###############################
					#!!!!here store the nodeInfo in final file!!!!
					################################
					snap.snap_swap(DataSet, this_index)
					################################
				result = {
					'from': this_index,
					'result': signal,
					'superstep' : GlobalInfo['superstep']
					}
				if signal=='success':
					result['rank'] = temprank
				print('worker-%d: Sent signal %s to master' % (this_index,signal))
				print("---------------------------------------")
				channel.basic_publish(exchange='',
                      routing_key='master',
                      body=json.dumps(result),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
		ch.basic_ack(delivery_tag = method.delivery_tag)

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

print ('worker-num: '+str(GlobalInfo['worker-num']))
#C= [NodeFile, DataFile, index, NodeinCount, NodeRankFile,DataSet]
C = init.command()
global this_index
this_index = C[2]
global ntTable
global nodeInfo
global temprank
global DataSet
ntTable = {}
nodeInfo = {}
temprank = {}
DataSet = C[5]
if not (os.path.exists(C[0]) and os.path.exists(C[3]) and os.path.exists(C[4])):
	N = init.createNode(C[0],C[1],this_index,GlobalInfo['worker-num'])
	print('nfCount: '+str(N[2]))
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
			f.write(str(i)+" 0.15\n")
			i += 1
		f.close
else:
	ntTable = init.readNode(C[0])
	#############################
	#recover from snapshot
	#############################
	snapFile = '../data/'+DataSet+'_'+str(this_index)+'.snap'
	if os.path.exists(snapFile):
		print('recover...')
		nodeInfo = snap.recoverNodeInfo(DataSet, this_index)
		print(nodeInfo)
	else:
		nodeInfo = init.readNodeinCount(C[3])
		nodeInfo = init.readNodeRank(C[4],nodeInfo)
print('ntTable: '+str(ntTable))
print('nodeInfo: '+str(nodeInfo))

for node in nodeInfo: #everytime temprank is start from 0.15, not only the first time
	temprank[int(node)] = 0.15 

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host= GlobalInfo['host']))
channel = connection.channel()

GlobalInfo['superstep'] = 0
resetInfo()

channel.queue_declare(queue='master', durable=True)
for i in range(0, GlobalInfo['worker-num']):
    channel.queue_declare(queue='worker-%d' % i, durable=True)
    
channel.basic_consume(callback,
                queue='worker-%d' % this_index)

print('worder%d: Start to listen to message queue...'% this_index)
channel.start_consuming()
