#coding:utf-8
import sys
import os
def command():
	args = sys.argv
	if len(args)==3:
		DataSet = args[1]
		index = int(args[2])
	else:
		DataSet = 'test'
		index = int(args[1])
	NodeFile = '../data/'+DataSet+'_'+str(index)+'.txt';
	DataFile = '../data/'+DataSet+'.txt'
	NodeinCount = '../data/'+DataSet+'_count_'+str(index)+'.txt'
	NodeRankFile = '../data/'+DataSet+'_rank_'+str(index)+'.txt'
	return [NodeFile,DataFile,index,NodeinCount,NodeRankFile,DataSet]

def createNode(NodeFile,DataFile,index,totalIndex):
	nFile = open(NodeFile,'w')
	maxnode = 0
	ntTable = {}
	# ntList = {}
	nfcount = {}

	raw = open(DataFile, 'r')
	raw_lines = []
	for line in raw:
		if (line.find('#') >= 0):
			continue
		raw_lines.append(line)
	for line in raw_lines:
		split_line = line.split('\t')
		node_from = int(split_line[0])
		node_to = int(split_line[1])
		if node_from > maxnode:
			maxnode = node_from
		if node_to > maxnode:
			maxnode = node_to
		if node_from % totalIndex == index:
			if (ntTable.get(node_from, -1) == -1):
				ntTable[node_from] = []
			else:
				ntTable[node_from].append(node_to)

			if (nfcount.get(node_from, -1) == -1):
				nfcount[node_from] = 0
		if node_to % totalIndex == index:
			if (ntTable.get(node_to, -1) == -1):
				ntTable[node_to] = []

			if (nfcount.get(node_to, -1) == -1):
				nfcount[node_to] = 0
			else:
				nfcount[node_to] += 1
	for key in ntTable:
		nFile.write(str(key)+':'+str(ntTable[key])[1:-1]+"\n")
	nFile.close()
	return [ntTable,nfcount,maxnode]


def readNode(NodeFile):
	with open(NodeFile,'r') as f:
		ntTable = {}
		# while True:
		# 	line=f.readline()
		# 	if line:
		# 		split = line.find(':')
		# 		node = int(line[0:split])
		# 		nodetoListstr = line[split+1:]
		# 		nodestrList = nodetoListstr.split(', ')
		# 		nodeList = []
		# 		for nodestr in nodestrList:
		# 			nodeList.append(int(nodestr))
		# 		ntTable[node]=nodeList
		# 	else:
		# 		break
		#print(ntTable)
		for line in f:
			split_line = line.split(':')
			node = int(split_line[0])
			node_str = split_line[1]
			node_to_list = node_str.split(', ')
			ntTable[node] = []
			for node_to in node_to_list:
				if (node_to != "\n"):
					ntTable[node].append(int(node_to))
		return ntTable

def  readNodeinCount(NodeinFile):
	with open(NodeinFile,'r') as f:
		inList={}
		while True:
			line=f.readline()
			if line:
				split = line.find(' ')
				node = int(line[0:split])
				nodein = int(line[split+1:])
				inList[node] = (nodein,0)
			else:
				break

		return inList

def  readNodeRank(NodeRankFile,table):
	with open(NodeRankFile,'r') as f:
		rankList={}
		while True:
			line=f.readline()
			if line:
				split = line.find(' ')
				node = int(line[0:split])
				rank = float(line[split+1:])
				if(table.get(node,-1)!=-1):
					table[node] = (table[node][0],rank)
			else:
				break

		return table








