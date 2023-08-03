#!/bin/bash

#Este é um facilitador. Você consegue incluir rapidamente as tags conforme a sua necessidade.

# Definindo a região
region="us-east-1"

# Solicitando ao usuário a escolha entre RDS e EC2
read -p "Deseja adicionar ou remover tags em instâncias RDS (r) ou instâncias EC2 (e)? " resource_type

if [ "$resource_type" = "r" ]; then
  # Execução para instâncias RDS
  # Listando as instâncias RDS
  instances=$(aws rds describe-db-instances --region $region | jq -r '.DBInstances[].DBInstanceIdentifier')

  # Solicitando ao usuário a tag a ser adicionada ou removida
  read -p "Digite a key da tag que deseja adicionar ou remover em todas as instâncias: " key
  read -p "Digite o valor da tag que deseja adicionar ou remover em todas as instâncias: " value
  read -p "Deseja adicionar (a) ou remover (r) a tag? " action

  if [ "$action" = "a" ]; then
    # Adicionando a tag em cada instância RDS
    tag="$key=$value"
    for instance in $instances; do
      aws rds add-tags-to-resource --resource-name "arn:aws:rds:$region:315631129281:db:$instance" --tags Key=$key,Value=$value --region $region
      echo "Tag $tag adicionada na instância RDS $instance"
    done
  elif [ "$action" = "r" ]; then
    # Removendo a tag de cada instância RDS
    tag="$key=$value"
    for instance in $instances; do
      aws rds remove-tags-from-resource --resource-name "arn:aws:rds:$region:315631129281:db:$instance" --tag-keys $key --region $region
      echo "Tag $tag removida da instância RDS $instance"
    done
  else
    echo "Opção inválida"
    exit 1
  fi

elif [ "$resource_type" = "e" ]; then
  # Execução para instâncias EC2
  # Listando as instâncias EC2
  instances=$(aws ec2 describe-instances --region $region | jq -r '.Reservations[].Instances[].InstanceId')

  # Solicitando ao usuário a tag a ser adicionada ou removida
  read -p "Digite a key da tag que deseja adicionar ou remover em todas as instâncias: " key
  read -p "Digite o valor da tag que deseja adicionar ou remover em todas as instâncias: " value
  read -p "Deseja adicionar (a) ou remover (r) a tag? " action

  if [ "$action" = "a" ]; then
    # Adicionando a tag em cada instância EC2
    tag="$key=$value"
    for instance in $instances; do
      aws ec2 create-tags --resources $instance --tags Key=$key,Value=$value --region $region
      echo "Tag $tag adicionada na instância EC2 $instance"
    done
  elif [ "$action" = "r" ]; then
    # Removendo a tag de cada instância EC2
    tag="$key=$value"
    for instance in $instances; do
      aws ec2 delete-tags --resources $instance --tags Key=$key --region $region
      echo "Tag $tag removida da instância EC2 $instance"
    done
  else
    echo "Opção inválida"
    exit 1
  fi

else
  echo "Opção inválida"
  exit 1
fi
