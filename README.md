# Start Stop RDS and EC2 com Tags
Este script em Python é executado como uma Lambda Function no AWS Lambda. Ele tem como objetivo iniciar e parar instâncias do Amazon RDS e instâncias EC2 de acordo com um determinado intervalo de tempo configurado como variáveis de ambiente na Lambda Function. O script filtra as instâncias por meio de suas tags e, em seguida, inicia ou para as instâncias elegíveis com base no horário atual.

# Configuração

O projeto utiliza o Serverless Framework para implantação da Lambda Function. Antes de executar a implantação, é necessário configurar as seguintes informações no arquivo serverless.yml:

1. Nome do Serviço e Provedor AWS:

```bash
service: start-stop-aws-rds-tags

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  role: arn:aws:iam::xxxxxxxxxxxxx:role/start-stop-role  # Substitua pelo ARN do IAM Role com as permissões necessárias
```
2. Variáveis de Ambiente:

```bash
  environment:
    START_TIME: '06:00'           # Horário de início do intervalo de tempo para iniciar as instâncias
    STOP_TIME: '20:00'            # Horário de término do intervalo de tempo para parar as instâncias
    TIMEZONE: 'America/Sao_Paulo' # Fuso horário usado para determinar os horários de início e término
```
3. Nível de Log para o CloudWatch Logs:

```bash
  logs:
    level: INFO
```

# Execução

O script filtra as instâncias por meio de suas tags com a chave "economia" e valor "ativo", e em seguida, inicia ou para as instâncias elegíveis com base no horário atual. As ações são agendadas para ocorrer nos dias úteis (de segunda a sexta-feira) de acordo com o cron configurado na seção functions do arquivo serverless.yml.

# Bibliotecas utilizadas

O projeto utiliza as seguintes bibliotecas Python:

> boto3: biblioteca para interagir com a AWS.
> os: biblioteca para acessar as variáveis de ambiente.
> logging: biblioteca para registrar informações de log.
> datetime: biblioteca para trabalhar com datas e horas.
> dateutil: biblioteca para trabalhar com fuso horário.

# Informação adicional

"Para adicionar ou remover a tag em todas as instâncias RDS e EC2 da conta e região específica em que você deseja executar o script Python, utilize o Shell Script tags.sh."

Também é necessário configurar corretamente a VPC a ser usada, tais como subnet no arquivo serverless. 

Atente-se a política necessária para o correto funcionamento do Lambda através da ROLE. Neste repositório você vai encontrar um exemplo de política que pode ser usada noemada como "policy-role-example.json".

# Executando a Implantação com o Serverless Framework

Para executar a implantação do projeto no AWS Lambda usando o Serverless Framework, siga os passos abaixo:

1. Instale o Serverless Framework globalmente em sua máquina, caso ainda não tenha feito:

```bash
npm install -g serverless
```
2. Navegue até o diretório do projeto e execute o seguinte comando para implantar a função no AWS Lambda:

```bash
sls deploy
```

3. O Serverless Framework irá implantar a função e configurar o agendamento de acordo com o cron especificado na seção functions do arquivo serverless.yml. No final da implantação, você verá a URL de invocação da função.

Lembre-se de configurar corretamente as variáveis de ambiente e as informações de rede (VPC) conforme mencionado na seção de configuração. Além disso, substitua xxxxxxxxxxxxx pelo número da sua conta da AWS no ARN do IAM Role.

Pronto! Agora você tem o projeto configurado para iniciar e parar as instâncias RDS e EC2 de acordo com as tags e o intervalo de tempo configurado usando o AWS Lambda e o Serverless Framework.

