##Distributed PageRank

this project is written in python
我已经把初始的部分写好啦~
代码在worker 的init.py中，函数部分应该没什么问题，对不起我今天下午一边学一边写，代码风格可能很丑，之前python的项目完全没有做过，很多东西可能不够好，哪里不好，我立刻改！

在worker.py中，你们已经可以看到init的结果。
我对worker的命令行说明一下
``` python
python worker.py web-Google 1 3
```
表示关于web-Google这个图，在有3个worker计算的时候，编号为1(从0开始)的worker的启动，也就是初始化

worker调用init,但是并不显示结果

为了调试的输入方便，我又生成了另外两种格式  **--python worker.py 1 3--**    这时候数据库默认为test

或者 **--python worker.py 1--** 这时候数据库默认为test, worker数目为3

---
**config文件配置基本变量**

worker/rabbitInfo.config文件的阅读，修改和书写，可以通过basicInfo.py中的函数来修改。使用方法在worker中给出示例，用来存储master的ip，所有worker的ip，worker的数量，这些信息是整个系统的，大家都是一样的。

**初始化之后可以得到两个个hash表**

ntTable 为node及其指向顶点的list。

nodeInfo 为node及其(入度值,当前rank），我把这两个值放到一起，为了减少hash表的内存空间消耗。


**data中的文件包括4种**

test.txt为原图，基于边，每一行两给数字 from to

test_rank.txt为分数表，每个节点对应自己的分数，从0开始到最大序号

test_i,存储ntTable的内容，表示i worker负责的节点的指向节点，为中断初始化节约时间

test_count_i,存储i worker负责的节点的入度值。

--------------------------------------------------------
### 刘沛东 6.28日更新
1）更新了master.py和config.txt两个文件，master和worker的配置都可以直接从config.txt里读，当然啦，大家可以往里面加自己需要的变量，读完之后都放在GlobalInfo里了

2） master.py可以直接工作，但是worker还没写完，估计得写完一起调

3）主要思路是每个程序都有一个消息队列，master的就叫master，worker的叫worker-0,worker-1... 处理程序是消息驱动的，收到消息之后根据内容来完成对应的工作

4) rabbitmq已经处理好自己挂掉时的消息恢复,每个python程序处理完消息之后需要显式声明消息已经被处理，否则该消息会被再接受一次，所以恢复起来很简单

5) 我写了一小段代码判断消息是否已经被处理，如果重复就扔掉，所以挂掉又被重启的程序可以放心大胆地发消息

6) 调用回调的机制是串行，一个消息没处理完之前不会处理下一个（我实验得到的），所以不必担心原子性
#### 消息的处理逻辑
```
master callback

if 收到完结消息或成功消息
	计数+1
	（成功消息+1）
	if 成功计数足够
		发送全体结束
		程序结束
	if 计数足够
		发送超级步开始
	

worker

起始发送一个完结消息

worker callback

if 收到开始消息或者他人的计算完毕消息
	if 未开始该超级步
		开始超级步
		发送计算完毕消息给其他人
	if 是计算完毕消息
		进行计算
		if 已收到所有人消息
			发送完结消息
if 收到结束消息
	退出程序
```
--------------------------------------------------------
### 梁竞月 6.29日更新

感觉worker部分除了关闭恢复，其他的部分都写完了，还没开始调试，估计会有些一些bug，今晚开始调试

####我来明确一下重要的数据结构。
master_globalInfo = {
	host :string, 表示RabbitMQ server所在的IP
	total_iteration :数字，表示pagerank要求的迭代次数
	finish :数字，表示当前这一超步，已经完成任务的worker数目，每当有一个没有统计过的worker发来消息，finish一定加1
	success :数字, 表示当前这一超步，以及完成最后一次计算的worker数目，只有当收到的未读消息result = ‘success'的时候，success才会+1
	worker_num :数字，表示master管理的worker的总数
	super_step :数字，记录计算的迭代次数
	0，1，，，worker_num-1:每一个数字记录着一个1和0，如果globa[i] = 1 代表iworker发来的消息在这一轮还没处理过； globa[i] = 0则表示已经处理过了，即使再有来自该worker的消息也是重复的不需要处理的。
}
worker_globalInfo = {
	host :string, 表示RabbitMQ server所在的IP
	total_iteration :数字，表示pagerank要求的迭代次数
	finish :数字，表示当前这一超步，收到的已经发消息的worker数目，每当有一个没有统计过的worker发来消息，finish一定加1
	worker_num :数字，表示共同工作的worker的总数，包括自己。
	super_step :数字，记录计算的迭代次数
	0，1，，，worker_num-1:每一个数字记录着一个1和0，如果globa[i] = 1 代表iworker发来的消息在这一轮还没处理过； globa[i] = 0 则表示已经处理过了，即使再有来自该worker的消息也是重复的不需要处理的。
}

message——Master2Worker = {
	from: 'master'
	instruction: ‘success'表示所有计算结束，可以退出程序；‘start’可以开始新一轮的计算
	superstep: 新一轮计算的superstep, 如果worker的superstep小于该值，应该立刻更新为该值。
}
message——Worker2Master = {
	from :i
	result :‘success’表示worker完成最后一次计算，‘finish‘表示worker，收集了所有其他worker的消息，完成了一次计算
	superstep :校验，worker发送自己当前的超步，master会用来校验
}
message——WorkerI2WorkerJ = {
	from: i
	instruction :'count'表示计算，这个量，我没用到，不过如果将来要加上数据库的协调，可以加上'deliver'这一种可能
	superstep :worker-i发送自己当前的超步，如果接受者j的超步小于该值，说明master的start消息晚了一点，不过没关系。
	rank: {
			node_1: 0.291
			node_2: 0.33
		}
		rank就是传递数据的主体了，rank是一个dictionary，表示i发给j的节点变更值。
}
####接下来的工作
1) 能在两台机器上运行起来，调通代码

2) 加入恢复机制

3) *考虑合并数据库。