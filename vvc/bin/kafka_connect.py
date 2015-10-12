#!/usr/bin/env python
# encoding: utf-8

# kafka_connect.py topicname pid_path

from pykafka import KafkaClient
import sys
import os
try:
    pipe_type = sys.argv[1]
except IndexError as e:
    pipe_type = "mpp_vv_pcweb"

# 将当前进程pid落地
try:
    pid_file = sys.argv[2]
    pid = os.getpid()
    cfp  = open(pid_file, 'a+')
    constr = str(pid) + "\n"
    cfp.write(constr)
    cfp.close()
except IndexError as e:
    pass

# 连接kafka，获取数据，并输出到stdout
client = KafkaClient(hosts="10.100.1.51:9092,10.100.1.52:9092,10.100.1.53:9092,10.100.1.54:9092")
topic  = client.topics[pipe_type]
balanced_consumer = topic.get_simple_consumer()
#balanced_consumer = topic.get_balanced_consumer(
#  consumer_group='testgroup',
#  auto_commit_enable=True,
#  zookeeper_connect='com.hunantv.stormnode3:2181,com.hunantv.stormnode2:2181,com.hunantv.stormnode1:2181,com.hunantv.stormnode5:2181,com.hunantv.stormnode4:2181'
#)
for message in balanced_consumer:
    if message is not None:
        try:
            print message.value
        except IOError:
            exit(0)
