# -*- coding: utf-8 -*-
import psycopg2
import pika
import json

class FiasService:

    def __init__(self, mq_host, mq_user, mq_passw, db_user, db_passw):
        # RabbitMQ connection
        cred = pika.PlainCredentials(mq_user, mq_passw)
        self.rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host, credentials=cred))
        self.rabbit_channel = self.rabbit_conn.channel()
        self.rabbit_channel.queue_declare(queue='fias_rpc')
        self.rabbit_channel.basic_consume(self.on_rpc, queue='fias_rpc')
        # PostgreSQL connection
        self.db_conn = psycopg2.connect(host='localhost', dbname='fias', user=db_user, password=db_passw)

    def __del__():
        self.rabbit_conn.close()
        self.db_conn.close()

    def on_rpc(self, ch, method, props, body):
        body  = json.loads(body)
        req = body['req']
        arg = body['arg']
        print(' [x] Got RPC request {}({})'.format(req, arg))  # DEBUG mode only!
        if req == 'name_by_guid':
            # search adr obj by aoguid, request is { req: '', arg: {r: '<region_code>', guid: '<aoguid>'}}
            curs = self.db_conn.cursor()
            tabname = 'addrobj_'+arg['r'] if arg['r'] else 'addrobj'
            curs.execute("""
                select a.aoguid, a.parentguid, a.formalname, a.shortname, a.aolevel, a.regioncode 
                from {} a where a.aoguid = %s  and a.enddate > now()""".format(tabname,), (arg['guid'],) )
            res = curs.fetchall()
            ret = ''
            for row in res: 
                print (row)
                ret = json.dumps(row)
            curs.close()
        # return results
        ch.basic_publish(
            exchange='',
            routing_key = props.reply_to,
            properties = pika.BasicProperties(correlation_id=props.correlation_id),
            body = ret )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        print(' [x] Start consuming...')
        self.rabbit_channel.start_consuming()


if __name__ == '__main__':
    rabbit_user = 'fias'
    rabbit_passw = 'robertmiller'
    rabbit_host = '188.227.17.138'
    db_user = 'fiasuser'
    db_passw = 'monciBik#13'
    srvc = FiasService(rabbit_host, rabbit_user, rabbit_passw, db_user, db_passw)
    srvc.start()
