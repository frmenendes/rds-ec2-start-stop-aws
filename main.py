import json
import boto3
import os
import logging
from datetime import datetime, time
from typing import List, Dict, Any
from dateutil import tz

# Configuração inicial do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)

def has_economy_tag(tags: List[Dict[str, str]], key: str, value: str) -> bool:
    """Verifica se a instância possui a tag economia:ativo."""
    return any(tag['Key'] == key and tag['Value'] == value for tag in tags)

def filter_instances_by_tag(client: Any, resource_type: str, key: str, value: str) -> List[Dict[str, Any]]:
    """Filtra instâncias EC2 ou RDS pela tag especificada."""
    filtered_instances = []
    if resource_type == 'ec2':
        reservations = client.describe_instances(Filters=[{'Name': f'tag:{key}', 'Values': [value]}])['Reservations']
        for reservation in reservations:
            for instance in reservation['Instances']:
                filtered_instances.append(instance)
    elif resource_type == 'rds':
        instances = client.describe_db_instances()['DBInstances']
        for instance in instances:
            tags = client.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])['TagList']
            if has_economy_tag(tags, key, value):
                filtered_instances.append(instance)
    return filtered_instances

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # Variáveis de ambiente
        local_tz = tz.gettz(os.environ['TIMEZONE'])
        start_time_str, stop_time_str = os.environ['START_TIME'], os.environ['STOP_TIME']
        logger.info(f"Configurações - Timezone: {os.environ['TIMEZONE']}, Start Time: {start_time_str}, Stop Time: {stop_time_str}")

        # Horários de início e parada
        start_time = datetime.strptime(start_time_str, '%H:%M').time().replace(tzinfo=local_tz)
        stop_time = datetime.strptime(stop_time_str, '%H:%M').time().replace(tzinfo=local_tz)
        now = datetime.now(tz=local_tz).time()

        # Ação baseada na hora atual
        action = 'start' if start_time <= now < stop_time else 'stop'
        logger.info(f"Ação determinada baseada na hora atual ({now}): {action}")

        # Clientes da AWS
        ec2_client = boto3.client('ec2')
        rds_client = boto3.client('rds')

        # Filtrar instâncias por tag
        ec2_instances = filter_instances_by_tag(ec2_client, 'ec2', 'economia', 'ativo')
        rds_instances = filter_instances_by_tag(rds_client, 'rds', 'economia', 'ativo')

        # Executar ações
        for instance in ec2_instances:
            instance_id = instance['InstanceId']
            try:
                if action == 'start':
                    ec2_client.start_instances(InstanceIds=[instance_id])
                else:
                    ec2_client.stop_instances(InstanceIds=[instance_id])
                logger.info(f"{action.capitalize()}ing EC2 instance: {instance_id}")
            except Exception as e:
                logger.error(f"Error {action}ing EC2 instance {instance_id}: {e}")

        for instance in rds_instances:
            instance_id = instance['DBInstanceIdentifier']
            try:
                if action == 'start':
                    rds_client.start_db_instance(DBInstanceIdentifier=instance_id)
                else:
                    rds_client.stop_db_instance(DBInstanceIdentifier=instance_id)
                logger.info(f"{action.capitalize()}ing RDS instance: {instance_id}")
            except Exception as e:
                logger.error(f"Error {action}ing RDS instance {instance_id}: {e}")

    except Exception as e:
        logger.error(f"Error in script execution: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Script executed successfully!')
    }
