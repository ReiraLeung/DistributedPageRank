import ConfigParser 
import time

def writeConf(basicInfo):
	config = ConfigParser.RawConfigParser()
	for key in basicInfo:
		config.set("basicInfo", str(key), str(basicInfo[key]))
	fp = open("./rabbitInfo.config", "w") 
	config.write(fp)

def readConf():
	config = ConfigParser.ConfigParser() 
  	config.read("./rabbitInfo.config") 
  	basicInfo = {}
  	basicInfo["master_host"] = config.get("basicInfo", "master_host")
  	basicInfo["total_workers"] = config.getint("basicInfo", "total_workers")
  	ipstr = config.get("basicInfo","workers_ip")
  	basicInfo["workers_ip"] = ipstr[1:len(ipstr)-1].replace("'","").split(',')
  	return basicInfo

def setConf(key,val,basicInfo):
	basicInfo[key] = val
	config = ConfigParser.ConfigParser() 
  	config.read("./rabbitInfo.config") 
	config.set("basicInfo",str(key),str(val))
	fp = open("./rabbitInfo.config", "w") 
	config.write(fp)

def setConf(key,val):
	config = ConfigParser.ConfigParser() 
  	config.read("./rabbitInfo.config") 
	config.set("basicInfo",str(key),str(val))
	fp = open("./rabbitInfo.config", "w") 
	config.write(fp)

basicInfo = readConf()

#workers = basicInfo["workers_ip"]
#print str(workers)
#workers[2] = "172.16.1.58"
#setConf("workers_ip",workers,basicInfo)

