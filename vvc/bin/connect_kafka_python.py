############################################################################
##
## Copyright (c) 2015 hunantv.com, Inc. All Rights Reserved
## $Id: connect_kafka.py,v 0.0 2015/10/22  dongjie Exp $
##
############################################################################
#
###
# # @file   connect_kafka.py
# # @author dongjie<dongjie@e.hunantv.com>
# # @date   2015/10/22
# # @brief
# #
# ##

import kafka
import sys
import logging
logging.basicConfig(level=logging.ERROR)


class ConnectKafka:
    """
    connect kafka
    """
    def __init__(self, hosts):
        """
        """
        self.hosts = hosts
        self.client = kafka.KafkaClient(hosts=self.hosts)

    def get_simple_consumer(self, topic_name, group_name):
        """
        """
        topics = self.client.topics
        if topic_name not in topics:
            return [-1, None]
        #simple_consumer = kafka.SimpleConsumer(self.client, group_name, topic_name, max_buffer_size=3276800, auto_commit=False)
        flag = True
        while flag:
            simple_consumer = kafka.MultiProcessConsumer(self.client, group_name, topic_name, max_buffer_size=3276800, num_procs=8, auto_offset_reset='smallest')
            for l in simple_consumer:
                if l is not None:
                    try:
                        #print l.message.value
                        print l.offset
                    except (IOError, ValueError):
                        print 'error'
            #time.sleep(600)
            flag = False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(0)
    (di, topic_name, group_name) = sys.argv
    connect_kafka = ConnectKafka("10.100.1.51:9092,10.100.1.52:9092,10.100.1.53:9092,10.100.1.54:9092")
    connect_kafka.get_simple_consumer(topic_name, group_name)
