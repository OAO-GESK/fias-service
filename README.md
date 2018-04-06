# Сервис получения сведений из адресного справочника ФИАС
- имя проекта: fias-service
- автор: max@huzm.ru
- дата: 2018

Источником данных является БД "fias" формата PostgreSQL, где имена полей таблиц совпадают с именами параметров объектов выгрузки ФИАС XML-формата.
Имена таблиц:
- addrobj: адресные объекты
- house: дома
- stead: земельные участки
- room: помещения

Сервиc работает по принципу RPC (remote procedure call) посредством брокера очередей RabbitMQ

## Требования
Python: 3.5+
- pika==0.11.2
- psycopg2==2.7.4
RabbitMQ: 3.5.7+

## Форматы запросов и ответов

### Запрос наименования адресного объекта по идентификатору AOGUID
RabbitMQ queue: *fias_rpc*
Request body: { "req" : "name_by_guid", "arg" : { "r" : <regioncode>, "guid" : <aoguid> } }
Response body: { "aoguid" : <aoguid>, "parentguid" : <parentguid>, "formalname" : <formalname>, "shortname" : <shortname>, "aolevel" : <aolevel>, "regioncode" : <regioncode> }
