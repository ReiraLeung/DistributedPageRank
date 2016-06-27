#coding:utf-8
import json, sys
import pika

def resetInfo():
    global GlobalInfo
    for i in range(0, GlobalInfo['worker-num']):
        GlobalInfo[i] = 1
    GlobalInfo['finish'] = 0
    GlobalInfo['success'] = 0

def callback(ch, method, properties, body):
    global GlobalInfo
    mesaage = json.loads(body)
    print(" [x] Received message from %r" % message['from'])
    if (message['superstep'] != GlobalInfo['superstep']
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('This message has some superstep errors!!')
        return
    GlobalInfo['finish'] += GlobalInfo[message['from']]
    if (message['result'] == 'success'):
        GlobalInfo['success'] += GlobalInfo[message['from']]
    GlobalInfo[message['from']] = 0
    
    if (GlobalInfo['success'] == GlobalInfo['worker-num']):
        result = {
            'from': 'master',
            'instruction': 'success',
            }
        for i in range(0, GlobalInfo['worker-num']):
            channel.basic_publish(exchange='',
                      routing_key='worker-%d' % i,
                      body=json.dumps(result),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
        print('[*]Master has finished all jobs, superstep: %d' % GlobalInfo['superstep'])
        ch.basic_ack(delivery_tag = method.delivery_tag)
        sys.exit()
        
    if (GlobalInfo['success'] == GlobalInfo['worker-num']):
        print('[*]Master has finished a superstep, superstep: %d' % GlobalInfo['superstep'])
        GlobalInfo['superstep'] += 1
        result = {
            'from': 'master',
            'instruction': 'start',
            'superstep' : GlobalInfo['superstep'],
            }
        
        for i in range(0, GlobalInfo['worker-num']):
            channel.basic_publish(exchange='',
                      routing_key='worker-%d' % i,
                      body=json.dumps(result),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
       
            
    
    ch.basic_ack(delivery_tag = method.delivery_tag)

error = 0
config_file = open('config.txt')
global GlobalInfo
try:
    GlobalInfo = json.loads( config_file.read( ))
except:
    print('Config File Error!')
    error = 1
finally:
    file_object.close( )
    if (error == 1):
        sys.exit()

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
                queue='master')

print(' [*] Master Start to listen to message queue...')
channel.start_consuming()
    
