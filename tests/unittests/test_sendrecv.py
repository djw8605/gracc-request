import json
import pika
import sys
import unittest
from datetime import datetime, timedelta
import string
import random


class TestSendRecv(unittest.TestCase):
    
    def _createName(self, size=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))
    
    def setUp(self):
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('localhost',
                                                5672, '/', credentials)
        self.conn = pika.adapters.blocking_connection.BlockingConnection(parameters)

        self.channel = self.conn.channel()


        self.msg = """
        {
          "kind": "raw",
          "filter": {
            "query": {
              "query_string": {
                "query": "vo=cms"
              }
            }
          }
        }
        """
        # Create the receive queue
        self.channel.queue_declare(queue='test_queue', durable=False, exclusive=True, auto_delete=True)
        self.channel.exchange_declare(exchange='test_exchange', exchange_type='direct', durable=False, auto_delete=True)
        self.channel.queue_bind(queue='test_queue', exchange='test_exchange', routing_key='test_key')
        
        # Create the control queue
        control_queue = "control-queue-%s" % self._createName()
        control_exchange = "control-exchange-%s" % self._createName()
        self.channel.queue_declare(queue=control_queue, durable=False, exclusive=True, auto_delete=True)
        self.channel.exchange_declare(control_exchange, exchange_type='direct', durable=False, auto_delete=True)
        self.channel.queue_bind(queue=control_queue, exchange=condor_exchange, routing_key=None)
        
        self.msg_json = json.loads(self.msg)
        # Set the destination
        self.msg_json['destination'] = 'test_exchange'
        self.msg_json['routing_key'] = 'test_key'
        self.msg_json['control'] = control_exchange
        
        # Set the timerange
        self.msg_json['to'] = str(datetime.utcnow())
        self.msg_json['from'] = str(datetime.utcnow() - timedelta(days=365))
    
    def test_sendrecv(self):
        status = {'body': "", 'control': ""}
        def getMessage(channel, method, properties, body):
            status['body'] = body
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
            self.channel.stop_consuming()
            
        def getControlMessage(channel, method, properties, body):
            status['control'] = body
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
            

        def deadline_reached():
            #print "Deadline reached"
            self.channel.stop_consuming()


        self.channel.basic_consume(getMessage, "test_queue")

        
        self.channel.basic_publish('gracc.osg.requests',
                              'gracc.osg.requests',
                              json.dumps(self.msg_json),
                              pika.BasicProperties(content_type='text/json',
                                                   delivery_mode=1))
        

                                                   
        self.conn.add_timeout(10, deadline_reached)   
        
        self.channel.start_consuming()

        self.assertGreater(len(status['body']), 0)
        self.assertGreater(len(status['control']), 0)
        
        self.conn.close()



                                           



    
                                        






