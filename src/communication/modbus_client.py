#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento de cliente Modbus TCP.
"""

import logging
import time
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

logger = logging.getLogger(__name__)

class ModbusClientManager:
    """
    Classe para gerenciar a comunicação Modbus TCP com um dispositivo remoto.
    
    Esta classe encapsula as funcionalidades da biblioteca pymodbus para
    facilitar a comunicação com dispositivos Modbus TCP, como o CLP Mitsubishi FX5U.
    """
    
    def __init__(self, host, port=502, timeout=3.0, retry_count=3, retry_delay=1.0, unit=1):
        """
        Inicializa o gerenciador de cliente Modbus.
        
        Args:
            host (str): Endereço IP ou hostname do servidor Modbus
            port (int): Porta TCP do servidor Modbus (padrão: 502)
            timeout (float): Tempo limite para operações em segundos
            retry_count (int): Número de tentativas de reconexão
            retry_delay (float): Atraso entre tentativas em segundos
            unit (int): ID da unidade/slave (padrão: 1)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.unit = unit
        self.client = None
    
    def connect(self):
        """
        Estabelece conexão com o servidor Modbus.
        
        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário
        """
        try:
            logger.info(f"Conectando ao servidor Modbus em {self.host}:{self.port}")
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            connected = self.client.connect()
            if connected:
                logger.info("Conexão estabelecida com sucesso")
                return True
            else:
                logger.error("Falha ao conectar ao servidor Modbus")
                return False
        except Exception as e:
            logger.exception(f"Erro ao conectar ao servidor Modbus: {e}")
            return False
    
    def disconnect(self):
        """
        Encerra a conexão com o servidor Modbus.
        
        Returns:
            bool: True se a desconexão foi bem-sucedida, False caso contrário
        """
        if self.client and self.client.is_socket_open():
            self.client.close()
            logger.info("Conexão Modbus encerrada")
            return True
        return False
    
    def _execute_with_retry(self, operation_func, *args, **kwargs):
        """
        Executa uma operação Modbus com tentativas de reconexão em caso de falha.
        
        Args:
            operation_func: Função de operação Modbus a ser executada
            *args: Argumentos posicionais para a função
            **kwargs: Argumentos nomeados para a função
            
        Returns:
            O resultado da operação ou None em caso de falha
        """
        for attempt in range(self.retry_count + 1):
            try:
                if not self.client or not self.client.is_socket_open():
                    logger.warning("Cliente não conectado. Tentando reconectar...")
                    if not self.connect():
                        logger.error("Falha na reconexão")
                        return None
                
                result = operation_func(*args, **kwargs)
                if hasattr(result, 'isError') and result.isError():
                    logger.error(f"Erro na operação Modbus: {result}")
                    return None
                return result
                
            except ConnectionException as e:
                logger.warning(f"Erro de conexão (tentativa {attempt+1}/{self.retry_count+1}): {e}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
                    self.disconnect()
                else:
                    logger.error("Número máximo de tentativas excedido")
                    return None
                    
            except ModbusException as e:
                logger.error(f"Erro Modbus: {e}")
                return None
                
            except Exception as e:
                logger.exception(f"Erro inesperado: {e}")
                return None
    
    def read_coils(self, address, count=1):
        """
        Lê o estado de coils (bobinas) do dispositivo Modbus.
        
        Args:
            address (int): Endereço inicial dos coils
            count (int): Número de coils a serem lidos
            
        Returns:
            list: Lista de estados dos coils (True/False) ou None em caso de falha
        """
        logger.debug(f"Lendo {count} coil(s) a partir do endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.read_coils,
            address,
            count=count,
            slave=self.unit
        )
        if result:
            return result.bits[:count]
        return None
    
    def read_discrete_inputs(self, address, count=1):
        """
        Lê o estado de entradas discretas do dispositivo Modbus.
        
        Args:
            address (int): Endereço inicial das entradas
            count (int): Número de entradas a serem lidas
            
        Returns:
            list: Lista de estados das entradas (True/False) ou None em caso de falha
        """
        logger.debug(f"Lendo {count} entrada(s) discreta(s) a partir do endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.read_discrete_inputs,
            address,
            count=count,
            slave=self.unit
        )
        if result:
            return result.bits[:count]
        return None
    
    def read_holding_registers(self, address, count=1):
        """
        Lê valores de holding registers do dispositivo Modbus.
        
        Args:
            address (int): Endereço inicial dos registros
            count (int): Número de registros a serem lidos
            
        Returns:
            list: Lista de valores dos registros ou None em caso de falha
        """
        logger.debug(f"Lendo {count} holding register(s) a partir do endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.read_holding_registers,
            address,
            count=count,
            slave=self.unit
        )
        if result:
            return result.registers
        return None
    
    def read_input_registers(self, address, count=1):
        """
        Lê valores de input registers do dispositivo Modbus.
        
        Args:
            address (int): Endereço inicial dos registros
            count (int): Número de registros a serem lidos
            
        Returns:
            list: Lista de valores dos registros ou None em caso de falha
        """
        logger.debug(f"Lendo {count} input register(s) a partir do endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.read_input_registers,
            address,
            count=count,
            slave=self.unit
        )
        if result:
            return result.registers
        return None
    
    def write_coil(self, address, value):
        """
        Escreve o estado de um coil no dispositivo Modbus.
        
        Args:
            address (int): Endereço do coil
            value (bool): Valor a ser escrito (True/False)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        logger.debug(f"Escrevendo valor {value} no coil de endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.write_coil,
            address,
            value,
            slave=self.unit
        )
        return result is not None
    
    def write_register(self, address, value):
        """
        Escreve um valor em um holding register do dispositivo Modbus.
        
        Args:
            address (int): Endereço do registro
            value (int): Valor a ser escrito (0-65535)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        logger.debug(f"Escrevendo valor {value} no registro de endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.write_register,
            address,
            value,
            slave=self.unit
        )
        return result is not None
    
    def write_registers(self, address, values):
        """
        Escreve valores em múltiplos holding registers do dispositivo Modbus.
        
        Args:
            address (int): Endereço inicial dos registros
            values (list): Lista de valores a serem escritos
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        logger.debug(f"Escrevendo {len(values)} valores a partir do endereço {address}")
        # Usando kwargs para compatibilidade com a API do pymodbus 3.8.6
        result = self._execute_with_retry(
            self.client.write_registers,
            address,
            values,
            slave=self.unit
        )
        return result is not None
