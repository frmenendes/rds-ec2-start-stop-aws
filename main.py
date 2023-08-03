import json
import boto3
import os
import logging
from datetime import datetime, time
from dateutil import tz

# Definindo as variáveis de start e stop (essas variaveis informam o intervalo de quando desligar e quando ligar)
local_tz = tz.gettz(os.environ['TIMEZONE'])

start_time = datetime.strptime(os.environ['START_TIME'], '%H:%M').time()
start_time = datetime.combine(datetime.today(), start_time)
start_time = start_time.replace(tzinfo=local_tz)

stop_time = datetime.strptime(os.environ['STOP_TIME'], '%H:%M').time()
stop_time = datetime.combine(datetime.today(), stop_time)
stop_time = stop_time.replace(tzinfo=local_tz)

# Configurando o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Criando um handler para enviar os logs para o CloudWatch
cw = boto3.client('logs')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# Listando as instâncias EC2
ec2_client = boto3.client('ec2')
list_ec2_instances = ec2_client.describe_instances()['Reservations']
all_ec2_instances = [instance for reservation in list_ec2_instances for instance in reservation['Instances']]

# Listando as instâncias RDS
rds_client = boto3.client('rds')
list_rds_instances = rds_client.describe_db_instances()['DBInstances']

# Definindo as tags e valores para filtrar as instâncias (adicione quantas tags quiser)
tags_to_check = {
    'economia': 'ativo',
    'outra_tag': 'valor_da_outra_tag'
}

# Filtrando as instâncias de acordo com o status e a hora atual
now = datetime.now(tz=local_tz).time()

# Verifica se é para iniciar ou parar as instâncias
if now >= start_time.time() and now < stop_time.time():
    action = True
else:
    action = False

# Função para verificar se a instância possui todas as tags e valores fornecidos
def has_all_tags(instance_tags, tags_to_check):
    for key, value in tags_to_check.items():
        if not any(tag['Key'] == key and tag['Value'] == value for tag in instance_tags):
            return False
    return True

# Filtrando as instâncias EC2 com as tags
eligible_ec2_instances = [instance for instance in all_ec2_instances
                          if has_all_tags(instance.get('Tags', []), tags_to_check) if tags_to_check else True]

# Filtrando as instâncias RDS com as tags e validando o Engine
eligible_rds_instances = [i for i in list_rds_instances 
                          if (has_all_tags(rds_client.list_tags_for_resource(ResourceName=i['DBInstanceArn'])['TagList'], tags_to_check) if tags_to_check else True)
                          and i['Engine'] not in ['aurora', 'aurora-mysql', 'aurora-postgresql'] 
                          and i['DBInstanceStatus'] == (action and 'stopped' or 'available')]

# Executando o start e stop das instâncias EC2
for instance in eligible_ec2_instances:
    instance_id = instance['InstanceId']
    status = instance['State']['Name']
    
    if (status == 'running' and action) or (status == 'stopped' and not action):
        logger.info(f'Instance already {status}: {instance_id}')
        continue

    if action and status == 'stopped':
        ec2_client.start_instances(InstanceIds=[instance_id])
        logger.info(f'Starting instance: {instance_id}')
    elif not action and status == 'running':
        ec2_client.stop_instances(InstanceIds=[instance_id])
        logger.info(f'Stopping instance: {instance_id}')
    else:
        logger.info(f'Instance {instance_id} already in the desired state')

# Executando o start e stop das instâncias RDS
for instance in eligible_rds_instances:
    status = instance['DBInstanceStatus']
    if (status == 'available' and action) or (status == 'stopped' and not action):
        logger.info(f'Instance already {status}: {instance["DBInstanceIdentifier"]}')
        continue

    if action and status == 'stopped':
        rds_client.start_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])
        logger.info(f'Starting instance: {instance["DBInstanceIdentifier"]}')
    elif not action and status == 'available':
        rds_client.stop_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])
        logger.info(f'Stopping instance: {instance["DBInstanceIdentifier"]}')
    else:
        logger.info(f'Instance {instance["DBInstanceIdentifier"]} already in the desired state')

# Retornando o status de execução
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Script executed successfully!')
    }
