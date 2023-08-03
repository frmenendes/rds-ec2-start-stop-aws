# Start Stop RDS Tags
Esse script em Python é executado como uma Lambda Function no AWS Lambda. Ele tem como objetivo iniciar e parar instâncias do Amazon RDS e instâncias EC2 de acordo com um determinado intervalo de tempo configurado como variáveis de ambiente na Lambda Function. O script filtra as instâncias por meio de suas tags e, em seguida, inicia ou para as instâncias elegíveis com base no horário atual.

# Configuração
Antes de executar a Lambda Function, é necessário configurar as seguintes variáveis de ambiente:

- START_TIME: horário de início do intervalo de tempo para iniciar as instâncias (formato HH:MM, exemplo: 06:00).
- STOP_TIME: horário de término do intervalo de tempo para parar as instâncias (formato HH:MM, exemplo: 20:00).
- TIMEZONE: fuso horário usado para determinar os horários de início e término (exemplo: America/Sao_Paulo).
- VPC_SECURITY_GROUP_IDS: IDs dos grupos de segurança da VPC em que as instâncias estão localizadas (exemplo: sg-0123456789abcdefg).
- VPC_SUBNET_IDS: IDs das sub-redes da VPC em que as instâncias estão localizadas (exemplo: subnet-0123456789abcdefg).
- LOG_LEVEL: nível de log para o CloudWatch Logs (exemplo: INFO).

# Execução
O script filtra as instâncias por meio de suas tags com a chave economia e valor ativo, e em seguida, inicia ou para as instâncias elegíveis com base no horário atual.

# Bibliotecas utilizadas
O script utiliza as seguintes bibliotecas Python:

- boto3: biblioteca para interagir com a AWS.
- os: biblioteca para acessar as variáveis de ambiente.
- logging: biblioteca para registrar informações de log.
- datetime: biblioteca para trabalhar com datas e horas.
- dateutil: biblioteca para trabalhar com fuso horário.

# Informação adicional
"Para adicionar ou remover a tag em todas as instâncias RDS da conta e região específica que você deseja executar o script Python, utilize o Shell Script tags.sh"
