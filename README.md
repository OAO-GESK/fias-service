# ������ ��������� �������� �� ��������� ����������� ����
- ��� �������: fias-service
- �����: max@huzm.ru
- ����: 2018

���������� ������ �������� �� "fias" ������� PostgreSQL, ��� ����� ����� ������ ��������� � ������� ���������� �������� �������� ���� XML-�������.
����� ������:
- addrobj: �������� �������
- house: ����
- stead: ��������� �������
- room: ���������

�����c �������� �� �������� RPC (remote procedure call) ����������� ������� �������� RabbitMQ

## ����������
Python: 3.5+
- pika==0.11.2
- psycopg2==2.7.4
RabbitMQ: 3.5.7+

## ������� �������� � �������

### ������ ������������ ��������� ������� �� �������������� AOGUID
RabbitMQ queue: *fias_rpc*
Request body: { "req" : "name_by_guid", "arg" : { "r" : <regioncode>, "guid" : <aoguid> } }
Response body: { "aoguid" : <aoguid>, "parentguid" : <parentguid>, "formalname" : <formalname>, "shortname" : <shortname>, "aolevel" : <aolevel>, "regioncode" : <regioncode> }
