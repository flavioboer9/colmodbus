#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de configuração para a aplicação de comunicação Modbus.
"""

# Configurações do cliente Modbus
MODBUS_HOST = "localhost"    # Endereço IP do servidor Modbus local
MODBUS_PORT = 5020           # Porta do servidor Modbus local
MODBUS_TIMEOUT = 3.0          # Timeout em segundos
MODBUS_RETRY_COUNT = 3        # Número de tentativas de reconexão
MODBUS_RETRY_DELAY = 1.0      # Delay entre tentativas em segundos

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "modbus_app.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# Mapeamento de registros Modbus baseado no mock server
# O mock server possui apenas holding registers com 3 variáveis
REGISTER_MAP = {
    # Holding Registers (hr)
    "ativar": {
        "address": 0,
        "count": 1,
        "type": "bool",
        "register_type": "holding"
    },
    "entregar": {
         "address": 1,
        "count": 1,
        "type": "bool",
        "register_type": "holding"
    },
    "gaveta": {
        "address": 2,
        "count": 1,
        "type": "uint16",
        "register_type": "holding"
    },
    "posicao_gaveta": {
        "address": 3,
        "count": 1,
        "type": "uint16",
        "register_type": "holding"
    }
}
