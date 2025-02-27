#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para manipulação de dados Modbus na camada de aplicação.
Adaptado para trabalhar com o servidor mock que utiliza posições específicas no vetor.
"""

import logging
from src.communication import ModbusClientManager
from src.utils import ModbusDataConverter
from src.config import REGISTER_MAP

logger = logging.getLogger(__name__)

class ModbusDataHandler:
    """
    Classe para manipulação de dados Modbus na camada de aplicação.
    
    Esta classe utiliza o ModbusClientManager para comunicação e
    o ModbusDataConverter para conversão de dados.
    
    Adaptada para trabalhar com o servidor mock que utiliza posições específicas:
    - Posição 0: ativar (bool)
    - Posição 1: entregar (bool)
    - Posição 2: gaveta (uint16)
    - Posição 3: posicao_gaveta (uint16)
    """
    
    def __init__(self, client_manager):
        """
        Inicializa o manipulador de dados Modbus.
        
        Args:
            client_manager (ModbusClientManager): Instância do gerenciador de cliente Modbus
        """
        self.client_manager = client_manager
        self.converter = ModbusDataConverter()
        
        # Mapeamento direto de tags para posições no vetor
        self.tag_positions = {
            "ativar": 0,
            "entregar": 1,
            "gaveta": 2,
            "posicao_gaveta": 3
        }
    
    def read_tag(self, tag_name):
        """
        Lê o valor de uma tag específica.
        
        Args:
            tag_name (str): Nome da tag a ser lida
            
        Returns:
            O valor da tag ou None em caso de falha
        """
        if tag_name not in REGISTER_MAP:
            logger.error(f"Tag {tag_name} não encontrada no mapeamento de registros")
            return None
        
        tag_config = REGISTER_MAP[tag_name]
        address = tag_config["address"]
        count = tag_config["count"]
        register_type = tag_config.get("register_type", "holding")  # Tipo padrão é holding register
        
        # Leitura baseada no tipo de registro
        if register_type == "input":
            raw_value = self.client_manager.read_input_registers(address, count)
        elif register_type == "coil":
            raw_value = self.client_manager.read_coils(address, count)
        elif register_type == "discrete_input":
            raw_value = self.client_manager.read_discrete_inputs(address, count)
        else:  # holding register (padrão)
            # Usar a posição específica no vetor para ler o valor
            position = self.tag_positions.get(tag_name, address)
            raw_value = self.client_manager.read_holding_registers(position, count)
        
        if raw_value is None:
            logger.error(f"Falha ao ler a tag {tag_name}")
            return None
        
        # Converter o valor bruto para o tipo apropriado
        try:
            if tag_config["type"] == "bool" or register_type in ["coil", "discrete_input"]:
                # Para coils e discrete inputs, retornamos diretamente o valor booleano
                return raw_value[0] if count == 1 else raw_value
            elif tag_config["type"] == "uint16":
                # Para registros de 16 bits, retornamos o valor inteiro
                return raw_value[0] if count == 1 else raw_value
            elif tag_config["type"] == "float":
                # Para valores de ponto flutuante, aplicamos a escala se definida
                scale = tag_config.get("scale", 1.0)
                value = raw_value[0] if count == 1 else raw_value
                return value * scale
            else:
                # Tipo desconhecido, retornar valor bruto
                logger.warning(f"Tipo de dados desconhecido para a tag {tag_name}: {tag_config['type']}")
                return raw_value
        except Exception as e:
            logger.exception(f"Erro ao converter valor para a tag {tag_name}: {e}")
            return None
    
    def read_all_tags(self):
        """
        Lê todas as tags definidas no mapeamento de registros.
        
        Returns:
            dict: Dicionário com os valores de todas as tags
        """
        result = {}
        for tag_name in REGISTER_MAP:
            result[tag_name] = self.read_tag(tag_name)
        return result
      
    def write_tag(self, tag_name, value):
        """
        Escreve um valor em uma tag específica.
        
        Args:
            tag_name (str): Nome da tag a ser escrita
            value: Valor a ser escrito
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if tag_name not in REGISTER_MAP:
            logger.error(f"Tag {tag_name} não encontrada no mapeamento de registros")
            return False
        
        tag_config = REGISTER_MAP[tag_name]
        address = tag_config["address"]
        register_type = tag_config.get("register_type", "holding")
        
        # Conversão do valor para o formato apropriado
        try:
            if register_type == "coil":
                # Converter para booleano para coils
                bool_value = bool(value)
                return self.client_manager.write_coil(address, bool_value)
            elif register_type == "holding":
                # Usar a posição específica no vetor para escrever o valor
                position = self.tag_positions.get(tag_name, address)
                
                # Verificar o tipo de dado para o holding register
                data_type = tag_config.get("type", "uint16")
                
                if data_type == "bool":
                    # Para valores booleanos em holding registers, escrevemos 1 ou 0
                    int_value = 1 if bool(value) else 0
                    return self.client_manager.write_register(position, int_value)
                elif data_type == "uint16":
                    # Converter para inteiro para registros
                    int_value = int(value)
                    return self.client_manager.write_register(position, int_value)
                elif data_type == "float":
                    # Converter float para o formato apropriado
                    scale = tag_config.get("scale", 1.0)
                    # Aplicar a escala corretamente: multiplicar pelo inverso da escala
                    int_value = int(float(value) / scale)
                    logger.debug(f"Escrevendo valor float {value} com escala {scale}, valor convertido: {int_value}")
                    return self.client_manager.write_register(position, int_value)
                else:
                    logger.error(f"Tipo de dados não suportado para escrita: {data_type}")
                    return False
            else:
                logger.error(f"Tipo de registro não suportado para escrita: {register_type}")
                return False
        except Exception as e:
            logger.exception(f"Erro ao converter valor para escrita na tag {tag_name}: {e}")
            return False
    
    def write_multiple_tags(self, tags_values):
        """
        Escreve valores em múltiplas tags.
        
        Args:
            tags_values (dict): Dicionário com os nomes das tags e seus valores
            
        Returns:
            dict: Dicionário com os resultados das operações de escrita
        """
        results = {}
        for tag_name, value in tags_values.items():
            results[tag_name] = self.write_tag(tag_name, value)
        return results
