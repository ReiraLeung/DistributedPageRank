##Distributed PageRank

this project is written in python
我已经把初始的部分写好啦~
代码在worker 的init.py中，函数部分应该没什么问题，对不起我今天下午一边学一边写，代码风格可能很丑，之前python的项目完全没有做过，很多东西可能不够好，哪里不好，我立刻改！

在worker.py中，你们已经可以看到init的结果。
我对worker或者说init的命令行说明一下
``` python
python worker.py web-Google 1 3
```
表示关于web-Google这个图，在有3个worker计算的时候，编号为1(从0开始)的worker的启动，也就是初始化

worker调用init，所以init.py也可以计算，但是并不显示结果

为了调试的输入方便，我又生成了另外两种格式  **--python worker.py 1 3--**    这时候数据库默认为test

或者 **--python worker.py 1--** 这时候数据库默认为test, worker数目为3

---

**初始化之后可以得到两个个hash表**

ntTable 为node及其指向顶点的list。

nodeInfo 为node及其(入度值,当前rank），我把这两个值放到一起，为了减少hash表的内存空间消耗。


**data中的文件包括4种**

test.txt为原图，基于边，每一行两给数字 from to

test_rank.txt为分数表，每个节点对应自己的分数，从0开始到最大序号

test_i,存储ntTable的内容，表示i worker负责的节点的指向节点，为中断初始化节约时间

test_count_i,存储i worker负责的节点的入度值。





