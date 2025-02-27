#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para conversão de dados entre registros Modbus e tipos Python.
"""

import logging
import struct

logger = logging.getLogger(__name__)

class ModbusDataConverter:
    """
    Classe para conversão de dados entre registros Modbus e tipos Python.
    
    Fornece métodos para converter registros Modbus (valores de 16 bits)
    em tipos Python como inteiros, floats, strings, etc.
    """
    
    @staticmethod
    def registers_to_uint16(registers):
        """
        Converte um registro Modbus em um inteiro sem sinal de 16 bits.
        
        Args:
            registers (list): Lista com um valor de registro
            
        Returns:
            int: Valor inteiro sem sinal de 16 bits
        """
        if not registers or len(registers) < 1:
            logger.error("Registros insuficientes para conversão para uint16")
            return None
        
        return registers[0] & 0xFFFF
    
    @staticmethod
    def registers_to_int16(registers):
        """
        Converte um registro Modbus em um inteiro com sinal de 16 bits.
        
        Args:
            registers (list): Lista com um valor de registro
            
        Returns:
            int: Valor inteiro com sinal de 16 bits
        """
        if not registers or len(registers) < 1:
            logger.error("Registros insuficientes para conversão para int16")
            return None
        
        value = registers[0] & 0xFFFF
        # Converter para valor com sinal (complemento de 2)
        if value & 0x8000:
            value = value - 0x10000
        
        return value
    
    @staticmethod
    def registers_to_uint32(registers):
        """
        Converte dois registros Modbus em um inteiro sem sinal de 32 bits.
        
        Args:
            registers (list): Lista com dois valores de registro
            
        Returns:
            int: Valor inteiro sem sinal de 32 bits
        """
        if not registers or len(registers) < 2:
            logger.error("Registros insuficientes para conversão para uint32")
            return None
        
        # Ordem big-endian (padrão Modbus)
        return (registers[0] << 16) | registers[1]
    
    @staticmethod
    def registers_to_int32(registers):
        """
        Converte dois registros Modbus em um inteiro com sinal de 32 bits.
        
        Args:
            registers (list): Lista com dois valores de registro
            
        Returns:
            int: Valor inteiro com sinal de 32 bits
        """
        if not registers or len(registers) < 2:
            logger.error("Registros insuficientes para conversão para int32")
            return None
        
        # Ordem big-endian (padrão Modbus)
        value = (registers[0] << 16) | registers[1]
        
        # Converter para valor com sinal (complemento de 2)
        if value & 0x80000000:
            value = value - 0x100000000
        
        return value
    
    @staticmethod
    def registers_to_float32(registers):
        """
        Converte dois registros Modbus em um valor de ponto flutuante de 32 bits.
        
        Args:
            registers (list): Lista com dois valores de registro
            
        Returns:
            float: Valor de ponto flutuante de 32 bits
        """
        if not registers or len(registers) < 2:
            logger.error("Registros insuficientes para conversão para float32")
            return None
        
        try:
            # Ordem big-endian (padrão Modbus)
            # Converter para bytes e usar struct.unpack
            bytes_value = struct.pack('>HH', registers[0], registers[1])
            return struct.unpack('>f', bytes_value)[0]
        except Exception as e:
            logger.exception(f"Erro ao converter registros para float32: {e}")
            return None
    
    @staticmethod
    def registers_to_bits(register):
        """
        Converte um registro Modbus em uma lista de 16 bits.
        
        Args:
            register (int): Valor do registro
            
        Returns:
            list: Lista de 16 valores booleanos
        """
        if register is None:
            logger.error("Registro inválido para conversão para bits")
            return None
        
        return [(register >> i) & 1 == 1 for i in range(16)]
    
    @staticmethod
    def uint16_to_register(value):
        """
        Converte um inteiro sem sinal de 16 bits em um registro Modbus.
        
        Args:
            value (int): Valor inteiro sem sinal de 16 bits
            
        Returns:
            int: Valor do registro Modbus
        """
        try:
            value = int(value) & 0xFFFF
            return value
        except Exception as e:
            logger.exception(f"Erro ao converter uint16 para registro: {e}")
            return None
    
    @staticmethod
    def int16_to_register(value):
        """
        Converte um inteiro com sinal de 16 bits em um registro Modbus.
        
        Args:
            value (int): Valor inteiro com sinal de 16 bits
            
        Returns:
            int: Valor do registro Modbus
        """
        try:
            # Converter valor com sinal para complemento de 2
            value = int(value)
            if value < 0:
                value = value + 0x10000
            return value & 0xFFFF
        except Exception as e:
            logger.exception(f"Erro ao converter int16 para registro: {e}")
            return None
    
    @staticmethod
    def uint32_to_registers(value):
        """
        Converte um inteiro sem sinal de 32 bits em dois registros Modbus.
        
        Args:
            value (int): Valor inteiro sem sinal de 32 bits
            
        Returns:
            list: Lista com dois valores de registro
        """
        try:
            value = int(value) & 0xFFFFFFFF
            # Ordem big-endian (padrão Modbus)
            high = (value >> 16) & 0xFFFF
            low = value & 0xFFFF
            return [high, low]
        except Exception as e:
            logger.exception(f"Erro ao converter uint32 para registros: {e}")
            return None
    
    @staticmethod
    def int32_to_registers(value):
        """
        Converte um inteiro com sinal de 32 bits em dois registros Modbus.
        
        Args:
            value (int): Valor inteiro com sinal de 32 bits
            
        Returns:
            list: Lista com dois valores de registro
        """
        try:
            # Converter valor com sinal para complemento de 2
            value = int(value)
            if value < 0:
                value = value + 0x100000000
            # Ordem big-endian (padrão Modbus)
            high = (value >> 16) & 0xFFFF
            low = value & 0xFFFF
            return [high, low]
        except Exception as e:
            logger.exception(f"Erro ao converter int32 para registros: {e}")
            return None
    
    @staticmethod
    def float32_to_registers(value):
        """
        Converte um valor de ponto flutuante de 32 bits em dois registros Modbus.
        
        Args:
            value (float): Valor de ponto flutuante de 32 bits
            
        Returns:
            list: Lista com dois valores de registro
        """
        try:
            # Ordem big-endian (padrão Modbus)
            # Converter para bytes usando struct.pack
            bytes_value = struct.pack('>f', float(value))
            high, low = struct.unpack('>HH', bytes_value)
            return [high, low]
        except Exception as e:
            logger.exception(f"Erro ao converter float32 para registros: {e}")
            return None
    
    @staticmethod
    def bits_to_register(bits):
        """
        Converte uma lista de até 16 bits em um registro Modbus.
        
        Args:
            bits (list): Lista de valores booleanos
            
        Returns:
            int: Valor do registro Modbus
        """
        try:
            if len(bits) > 16:
                logger.error("Número de bits excede o limite de 16")
                return None
            
            register = 0
            for i, bit in enumerate(bits):
                if bit:
                    register |= (1 << i)
            return register
        except Exception as e:
            logger.exception(f"Erro ao converter bits para registro: {e}")
            return None
