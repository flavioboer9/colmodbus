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
│   ├── main.py            # Ponto de entrada principal da aplicação
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

## Configuração do Ambiente

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### Executando a Aplicação Principal

```bash
# Usando as configurações padrão (localhost:5020)
python src/main.py

# Especificando um servidor diferente
python src/main.py --host 192.168.1.10 --port 502

# Escrevendo valores nas tags
python src/main.py --new-ativar true --new-entregar false --new-gaveta 5
```

### Executando o Servidor Mock para Testes

```bash
# Iniciar o servidor mock na porta padrão (5020)
python src/start_mock_server.py

# Especificar um endereço/porta diferente
python src/start_mock_server.py 192.168.1.100 5000
```

## Configuração VS Code

O projeto inclui configurações para depuração no VS Code. Você pode iniciar o servidor mock ou executar o arquivo atual usando as configurações de lançamento predefinidas.

## Logs

Os logs da aplicação são armazenados em `modbus_app.log` e contêm informações detalhadas sobre a comunicação Modbus, incluindo conexões, leituras, escritas e erros.
