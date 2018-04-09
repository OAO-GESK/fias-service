# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
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
        ret = None
        print(' [x] Got RPC request {}({})'.format(req, arg))  # DEBUG mode only!
        if req == 'name_by_guid':
            # search adr obj by aoguid, request is  arg: {r: '<region_code>', guid: '<aoguid>'}
            curs = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            tabname = 'addrobj_'+arg['r'] if arg['r'] else 'addrobj'
            try:
                curs.execute("""
                    select a.aoguid, a.parentguid, a.formalname, a.shortname, a.aolevel, a.regioncode 
                    from {} a where a.aoguid = %s  and a.enddate > now() limit 1""".format(tabname,), (arg['guid'],) )
                res = curs.fetchone()
                if res:
                    res['result'] = 'ok'
                    ret = json.dumps(res)
                else: 
                    ret = json.dumps( {'result': 'notfound'} )
            except Exception as e:
                print(e)  # DEBUG
                ret = json.dumps( {'result': 'error'} )
                self.db_conn.rollback()
            print('Response: ') # DEBUG
            print(ret)
            curs.close()
        elif req == 'guids_by_name':
            # search addr objects match to given name
            pass
        # return results
        if not ret:
            ret = 'ERROR: Incorrect request!'
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
