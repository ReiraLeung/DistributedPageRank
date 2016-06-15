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
	Nodefile = '../data/'+DataSet+'_'+str(index)+'.txt';
	Datafile = '../data/'+DataSet+'.txt'
	return [Nodefile,Datafile,index,totalIndex]

def createNode(Nodefile,Datafile,index,totalIndex):
	nfile = open(Nodefile,'w')
	with open(Datafile,'r') as f:
		n = -1
		ntTable = {-1:['-1']}
		ntlist = []
		while True:
			line=f.readline()
			if line:
				if (line.find('#')>=0):
					continue
				split = line.find('\t')
				nf = line[0:split]
				nfi = int(nf)
				#print(index)
				if nfi%totalIndex == index:
					nti = int(line[split+1:])
					#print(str(nfi) + " "+ str(index)+" "+str(nti)+" "+str(n))
					if nfi!=n:
						ntTable[n] = ntlist
						n = nfi
						ntlist=[nti]
					else:
						ntlist.append(nti)
			else:
				ntTable[n] = ntlist
				break
		ntTable.pop(-1)
		for key in ntTable:
			nfile.write(str(key)+":"+str(ntTable[key])[1:-1]+"\n")
		nfile.close()
		return ntTable

def readNode(Nodefile):
	with open(Nodefile,'r') as f:
		ntTable = {}
		while True:
			line=f.readline()
			if line:
				split = line.find(':')
				node = int(line[0:split])
				nodetoliststr = line[split+1:]
				nodestrlist = nodetoliststr.split(', ')
				nodelist = []
				for nodestr in nodestrlist:
					nodelist.append(int(nodestr))
				ntTable[node]=nodelist
			else:
				break
		#print(ntTable)
		return ntTable

C= command()
print(C[0],C[1],C[2],C[3])
ntTable = {}
if not os.path.exists(C[0]):
	ntTable = createNode(C[0],C[1],C[2],C[3])
else:
	ntTable = readNode(C[0])
#print(ntTalbe)



