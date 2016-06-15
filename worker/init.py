import sys
import os
def command():
	args = sys.argv
	if len(args)==4:
		DataSet = args[1]
		index = int(args[2])
		totalIndex = int(args[3])
	elif len(args)==3:
		DataSet = 'test'
		index = int(args[1])
		totalIndex = int(args[2])
	else:
		DataSet = 'test'
		index = int(args[1])
		totalIndex = 3
	NodeFile = '../data/'+DataSet+'_'+str(index)+'.txt';
	DataFile = '../data/'+DataSet+'.txt'
	NodeinCount = '../data/'+DataSet+'_count_'+str(index)+'.txt'
	NodeRankFile = '../data/'+DataSet+'_rank.txt'
	return [NodeFile,DataFile,index,totalIndex,NodeinCount,NodeRankFile]

def createNode(NodeFile,DataFile,index,totalIndex):
	nFile = open(NodeFile,'w')
	maxnode = 0
	with open(DataFile,'r') as f:
		n = -1
		ntTable = {}
		ntList = {}
		nfcount = {}
		while True:
			line=f.readline()
			if line:
				if (line.find('#')>=0):
					continue
				split = line.find('\t')
				nf = line[0:split]
				nfi = int(nf)
				nti = int(line[split+1:])
				if nfi>maxnode:
					maxnode = nfi
				if nti>maxnode:
					maxnode = nti
				if(nfcount.get(nti,-1)==-1):
					nfcount[nti]=1
				else:
					nfcount[nti] +=1
				#print(index)
				if nfi%totalIndex == index:
					#print(str(nfi) + " "+ str(index)+" "+str(nti)+" "+str(n))
					if nfi!=n:
						ntTable[n] = ntList
						n = nfi
						ntList=[nti]
					else:
						ntList.append(nti)
			else:
				ntTable[n] = ntList
				break
		ntTable.pop(-1)
		for key in ntTable:
			nFile.write(str(key)+":"+str(ntTable[key])[1:-1]+"\n")
		nFile.close()
		return [ntTable,nfcount,maxnode]


def readNode(NodeFile):
	with open(NodeFile,'r') as f:
		ntTable = {}
		while True:
			line=f.readline()
			if line:
				split = line.find(':')
				node = int(line[0:split])
				nodetoListstr = line[split+1:]
				nodestrList = nodetoListstr.split(', ')
				nodeList = []
				for nodestr in nodestrList:
					nodeList.append(int(nodestr))
				ntTable[node]=nodeList
			else:
				break
		#print(ntTable)
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



C= command()
#print(C[0],C[1],C[2],C[3])
ntTable = {}
nodeInfo = {}
if not (os.path.exists(C[0]) and os.path.exists(C[4]) and os.path.exists(C[5])):
	N = createNode(C[0],C[1],C[2],C[3])
	print(N[2])
	ntTable = N[0]

	f = open(C[4],'w')
	for key in ntTable:
		nodeInfo[key] = (N[1][key], 0.15)
		f.write(str(key)+" "+str(N[1][key])+"\n")
	f.close()
	if not os.path.exists(C[5]):
		f = open(C[5],'w')
		i=0
		while i<=N[2]:
			f.write(str(i)+" 0.15\n")
			i += 1
		f.close
else:
	ntTable = readNode(C[0])
	nodeInfo = readNodeinCount(C[4])
	nodeInfo = readNodeRank(C[5],nodeInfo)




