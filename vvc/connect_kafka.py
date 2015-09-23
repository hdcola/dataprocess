#!/usr/bin/env python
# encoding: utf-8

from pykafka import KafkaClient
import sys
try:
    pipe_type = sys.argv[1]
except IndexError as e:
    pipe_type = "mpp_vv_pcweb"

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
        print message.value
