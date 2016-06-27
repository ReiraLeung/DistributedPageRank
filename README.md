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

### 接下来工作提示

1)首先是worker 启动之后，发给master一个启动消息，master收到所有worker的启动消息之后，会发送统一设置信息，即，master会给所有的worker发送自己的ip，其他worker的数目，以及其他所有worker 的IP；

2)worker收到消息之后，更改config内容，回复master可以开始第一轮计算了；

3)master收到所有worker的确认消息之后，发送给所有worker开始计算的命令；

4)收到开始命令的worker开始把自己的rank发送出去，原则上，同一个worker直接改内存，其他的根据目标节点，分别存储，所有节点都发一遍之后，打个包，给别的worker统一发过去，同时接收自己的包，把包中的消息一一接收；

5)worker确定收到所有的消息之后，计算pagerank，然后发送给master计算完毕的消息；

6）master收到所有完成的消息，就发一个广播，告诉大家要做checkpoint，记录轮回的次数；

7）然后所有worker刷一遍内存，完成后发消息给master， 然后回到第(3)步；

8）一旦，某个worker被关闭了，在某一步没有收到统一消息的master，就会告诉所有的worker恢复上一步的状态，并重新发送在线消息。该worker 重启之后，通知master已经重启，回到第(2)步。

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


