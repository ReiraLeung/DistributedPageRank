import init
import basicInfo
import sys
import os

BI = basicInfo.basicInfo
print str(BI)
#C= [NodeFile, DataFile, index, totalIndex, NodeinCount, NodeRankFile]
C = init.command(BI)

ntTable = {}
nodeInfo = {}
if not (os.path.exists(C[0]) and os.path.exists(C[4]) and os.path.exists(C[5])):
	N = init.createNode(C[0],C[1],C[2],C[3])
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
	ntTable = init.readNode(C[0])
	nodeInfo = init.readNodeinCount(C[4])
	nodeInfo = init.readNodeRank(C[5],nodeInfo)

print(str(ntTable))
print(str(nodeInfo))

