#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar um servidor Modbus mock para testes, focado apenas em holding registers.
"""

import sys
import os
import logging
import time
import threading
import socket
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# Adicionar o diretório raiz ao path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Variável global para armazenar o contexto do servidor e o slave
server_context = None
slave_context = None

# Valores iniciais para os registros
INITIAL_VALUES = {
    0: 0,  # Ativar: False (0)
    1: 1,  # Entregar: True (1)
    2: 7,  # Gaveta: 7
    3: 3   # Posição_Gaveta: 3
}

def is_port_in_use(host, port):
    """
    Verifica se uma porta está em uso.
    
    Args:
        host (str): Endereço IP
        port (int): Número da porta
        
    Returns:
        bool: True se a porta estiver em uso, False caso contrário
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def log_register_values():
    """
    Função para logar periodicamente os valores dos registros.
    """
    global slave_context
    
    if slave_context is None:
        logger.error("Contexto do slave não disponível para logging")
        return
    
    try:
        # Ler os valores atuais dos registros diretamente do contexto do slave
        hr_values = []
        for i in range(4):  # Lendo os 4 primeiros registros
            # Usar o método getValues com o tipo de registro correto (3 = Holding Registers)
            value = slave_context.getValues(3, i, 1)[0]
            hr_values.append(value)
        
        # Logar os valores com informações detalhadas
        logger.info("=== VALORES ATUAIS DOS REGISTROS ===")
        logger.info(f"    Ativar (0): {bool(hr_values[0])} ({hr_values[0]})")
        logger.info(f"    Entregar (1): {bool(hr_values[1])} ({hr_values[1]})")
        logger.info(f"    Gaveta (2): {hr_values[2]}")
        logger.info(f"    Posição_Gaveta (3): {hr_values[3]}")
        
        # Logar o array completo para debug
        logger.debug(f"Array completo de valores: {hr_values}")
    except Exception as e:
        logger.exception(f"Erro ao ler valores dos registros: {e}")
    
    # Agendar a próxima execução em 30 segundos
    threading.Timer(30.0, log_register_values).start()

def update_callback(address, value):
    """
    Callback para atualização de valores nos registros.
    
    Args:
        address (int): Endereço do registro
        value: Novo valor
    """
    logger.info(f"Registro {address} atualizado para {value}")
    
    # Mapear o endereço para o nome da tag
    tag_names = {
        0: "Ativar",
        1: "Entregar",
        2: "Gaveta",
        3: "Posição_Gaveta"
    }
    
    tag_name = tag_names.get(address, f"Desconhecido({address})")
    
    # Logar informações adicionais para tags booleanas
    if address in [0, 1]:
        logger.info(f"Tag {tag_name} atualizada para: {bool(value)} ({value})")
    else:
        logger.info(f"Tag {tag_name} atualizada para: {value}")
    
    return

class CustomModbusSlaveContext(ModbusSlaveContext):
    """
    Classe personalizada que estende ModbusSlaveContext para adicionar callbacks
    quando os valores são alterados.
    """
    
    def __init__(self, *args, **kwargs):
        """Inicializa o contexto com os argumentos padrão."""
        super().__init__(*args, **kwargs)
        self.update_callback = None
    
    def setValues(self, fx_code, address, values):
        """
        Sobrescreve o método setValues para adicionar um callback.
        
        Args:
            fx_code (int): O código da função Modbus
            address (int): O endereço do registro
            values (list): Os valores a serem definidos
        """
        # Chamar o método original
        super().setValues(fx_code, address, values)
        
        # Chamar o callback, se definido
        if self.update_callback is not None and fx_code == 3:  # 3 = Holding Registers
            for i, value in enumerate(values):
                self.update_callback(address + i, value)

def run_mock_server(host="localhost", port=5020):
    """
    Inicia um servidor Modbus mock para testes, focado apenas em holding registers.
    
    Args:
        host (str): Endereço IP para o servidor
        port (int): Porta para o servidor
    """
    global server_context, slave_context
    
    # Verificar se a porta já está em uso
    if is_port_in_use(host, port):
        logger.error(f"A porta {port} já está em uso. Não é possível iniciar o servidor.")
        logger.error("Encerre o servidor existente antes de iniciar um novo.")
        sys.exit(1)
    
    # Definir tamanho do bloco de registros
    block_size = 100
    
    # Gerar valores iniciais para os holding registers
    hr_values = [0] * block_size
    
    # Configurar valores iniciais para os registros
    for address, value in INITIAL_VALUES.items():
        hr_values[address] = value
    
    logger.info(f"Array de valores iniciais: {hr_values[:10]}")
    
    # Criar contexto do slave personalizado com callback
    slave_context = CustomModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, hr_values)  # Holding Registers
    )
    
    # Verificar valores iniciais no contexto
    context_values = []
    for i in range(4):
        context_values.append(slave_context.getValues(3, i, 1)[0])
    logger.info(f"Valores iniciais no contexto: {context_values}")
    
    # Corrigir os valores no contexto se necessário
    if context_values != [hr_values[0], hr_values[1], hr_values[2], hr_values[3]]:
        logger.warning("Valores no contexto não correspondem aos valores iniciais. Corrigindo...")
        slave_context.setValues(3, 0, [hr_values[0]])  # Ativar
        slave_context.setValues(3, 1, [hr_values[1]])  # Entregar
        slave_context.setValues(3, 2, [hr_values[2]])  # Gaveta
        slave_context.setValues(3, 3, [hr_values[3]])  # Posição_Gaveta
        
        # Verificar novamente
        context_values = []
        for i in range(4):
            context_values.append(slave_context.getValues(3, i, 1)[0])
        logger.info(f"Valores corrigidos no contexto: {context_values}")
    
    # Definir o callback para atualizações
    slave_context.update_callback = update_callback
    
    # Criar contexto do servidor com o slave
    server_context = ModbusServerContext(slaves=slave_context, single=True)
    
    # Configurar informações de identificação do dispositivo
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Modbus Mock Server'
    identity.ProductCode = 'MOCK-SERVER'
    identity.VendorUrl = 'https://github.com/pymodbus-dev/pymodbus'
    identity.ProductName = 'Modbus Server'
    identity.ModelName = 'Mock Server'
    identity.MajorMinorRevision = '1.0'
    
    # Iniciar o servidor
    logger.info(f"Iniciando servidor Modbus mock em {host}:{port}")
    logger.info("Modo: Apenas Holding Registers")
    logger.info("Valores iniciais configurados:")
    logger.info(f"  Holding Registers:")
    logger.info(f"    Ativar (0): {bool(context_values[0])} ({context_values[0]})")
    logger.info(f"    Entregar (1): {bool(context_values[1])} ({context_values[1]})")
    logger.info(f"    Gaveta (2): {context_values[2]}")
    logger.info(f"    Posição_Gaveta (3): {context_values[3]}")
    logger.info("Pressione Ctrl+C para parar o servidor")
    
    # Iniciar o timer para logar periodicamente os valores
    # Aguardar 5 segundos antes do primeiro log para garantir que o servidor esteja pronto
    threading.Timer(5.0, log_register_values).start()
   
    # Iniciar o servidor
    try:
        StartTcpServer(
            context=server_context,
            identity=identity,
            address=(host, port)
        )
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.exception(f"Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
    try:
        # Obter host e porta dos argumentos da linha de comando, se fornecidos
        host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5020
        
        # Iniciar o servidor
        run_mock_server(host, port)
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.exception(f"Erro ao iniciar o servidor: {e}")
