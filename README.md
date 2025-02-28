# ModbusIntegration

Projeto para comunicação entre um Raspberry Pi (Linux) e um CLP Mitsubishi FX5U via Modbus TCP utilizando a biblioteca pymodbus.

## Descrição do Projeto

Este projeto implementa uma solução para comunicação Modbus TCP entre um Raspberry Pi e um CLP Mitsubishi FX5U, permitindo a leitura e escrita de registradores específicos. O sistema é focado na manipulação das tags `ativar`, `entregar`, `gaveta` e `posicao_gaveta`.

## Estrutura do Projeto

```
modbus/
├── .vscode/               # Configurações do VS Code
├── docs/                  # Documentação do projeto
│   └── usage_guide.md     # Guia de uso detalhado
├── modbus/                # Ambiente virtual Python (pode ser ignorado)
├── src/                   # Código fonte do projeto
│   ├── application/       # Lógica de negócio e processamento de dados
│   ├── communication/     # Módulos de comunicação com pymodbus
│   ├── utils/             # Funções utilitárias
│   ├── config.py          # Configurações do sistema
│   ├── write_values.py    # Script para escrita de valores no servidor Modbus
│   └── start_mock_server.py # Servidor Modbus simulado para testes
├── modbus_app.log         # Arquivo de log da aplicação
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo
```

## Funcionalidades

- Comunicação Modbus TCP com dispositivos compatíveis
- Leitura e escrita de holding registers
- Conversão de tipos de dados (booleanos, inteiros)
- Servidor Modbus mock para testes sem hardware real
- Sistema de logging para monitoramento e diagnóstico

## Requisitos

- Python 3.8 ou superior
- pymodbus >= 3.8.0
- streamlit >= 1.32.0

## Instalação no Ubuntu Linux

Siga os passos abaixo para instalar e configurar o projeto em uma máquina com Ubuntu Linux:

```bash
# 1. Atualizar os repositórios do sistema
sudo apt update
sudo apt upgrade -y

# 2. Instalar o Git (necessário para clonar o repositório)
sudo apt install -y git

# 3. Instalar um navegador web (Firefox)
sudo apt install -y firefox

# 4. Instalar o Python e pip
sudo apt install -y python3 python3-pip

# 5. Instalar dependências do sistema necessárias
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# 6. Criar diretório para o projeto
mkdir -p ~/colmodbus
cd ~/colmodbus

# 7. Clonar o repositório
git clone https://github.com/flavioboer9/colmodbus.git .

# 8. Instalar as dependências do projeto
pip3 install -r requirements.txt

# 9. Tornar os scripts executáveis
chmod +x src/write_values.py
chmod +x src/start_mock_server.py
```

## Uso

### Executando a Aplicação Streamlit

```bash
# Iniciar a interface web Streamlit
streamlit run app.py --server.address 0.0.0.0

# Acessar a interface através do navegador em:
# http://localhost:8501

# Ou iniciar o Firefox diretamente na URL do Streamlit (em outro terminal)
firefox http://localhost:8501
```

### Executando a Aplicação Principal via Linha de Comando

```bash
# Usando as configurações padrão (localhost:5020)
python3 src/write_values.py

# Especificando um servidor diferente
python3 src/write_values.py --host 192.168.1.10 --port 502

# Escrevendo valores nas tags
python3 src/write_values.py --new-ativar true --new-entregar false --new-gaveta 5
```

### Executando o Servidor Mock para Testes

```bash
# Iniciar o servidor mock na porta padrão (5020)
python3 src/start_mock_server.py

# Especificar um endereço/porta diferente
python3 src/start_mock_server.py 192.168.1.100 5000
```

## Configuração VS Code

O projeto inclui configurações para depuração no VS Code. Você pode iniciar o servidor mock ou executar o arquivo atual usando as configurações de lançamento predefinidas.

## Logs

Os logs da aplicação são armazenados em `modbus_app.log` e contém informações detalhadas sobre a comunicação Modbus, incluindo conexões, leituras, escritas e erros.


github: https://github.com/dmin/modbus