#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo principal para a comunicação Modbus TCP entre Raspberry Pi e CLP Mitsubishi FX5U.
Focado na leitura e escrita das tags ativar, entregar, gaveta e posicao_gaveta.
"""

import logging
import sys
import os
import argparse

# Adiciona o diretório pai ao path para importar os módulos do projeto
# Isso é necessário quando executamos o script diretamente
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.communication import ModbusClientManager
from src.utils import setup_logging
from src.application import ModbusDataHandler
from src.config import MODBUS_HOST, MODBUS_PORT, MODBUS_TIMEOUT, MODBUS_RETRY_COUNT, MODBUS_RETRY_DELAY

def write_values():
    """Função principal do programa."""
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Comunicação Modbus para leitura e escrita de tags")
    parser.add_argument("--host", default=MODBUS_HOST, help="Endereço do servidor Modbus")
    parser.add_argument("--port", type=int, default=MODBUS_PORT, help="Porta do servidor Modbus")
    parser.add_argument("--new-ativar", type=str, help="Novo valor para a tag 'ativar' (true/false)")
    parser.add_argument("--new-entregar", type=str, help="Novo valor para a tag 'entregar' (true/false)")
    parser.add_argument("--new-gaveta", type=int, help="Novo valor para a tag 'gaveta'")
    parser.add_argument("--new-posicao-gaveta", type=int, help="Novo valor para a tag 'posicao_gaveta'")
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Iniciando aplicação de comunicação Modbus")
    logger.info(f"Conectando ao servidor Modbus em {args.host}:{args.port}")
    
    try:
        # Inicializar o cliente Modbus usando valores dos argumentos ou config.py
        client_manager = ModbusClientManager(
            host=args.host,
            port=args.port,
            timeout=MODBUS_TIMEOUT,
            retry_count=MODBUS_RETRY_COUNT,
            retry_delay=MODBUS_RETRY_DELAY
        )
        
        # Conectar ao servidor Modbus
        if client_manager.connect():
            logger.info("Conexão Modbus estabelecida com sucesso")
            
            # Criar o handler para manipulação dos dados
            handler = ModbusDataHandler(client_manager)

            logger.info("\nLendo tags de holding registers:")
            for tag_name in ["ativar", "entregar", "gaveta", "posicao_gaveta"]:
                value = handler.read_tag(tag_name)
                logger.info(f"  {tag_name}: {value}")
            
            # Processar novos valores, se fornecidos
            if any([args.new_ativar is not None, args.new_entregar is not None, 
                   args.new_gaveta is not None, args.new_posicao_gaveta is not None]):
                logger.info("=== Escrevendo novos valores ===")
                
                # Processar novo valor para 'ativar'
                if args.new_ativar is not None:
                    old_ativar = handler.read_tag("ativar")
                    new_ativar = args.new_ativar.lower() in ["true", "t", "1", "yes", "y"]
                    result = handler.write_tag("ativar", new_ativar)
                    if result:
                        current_value = handler.read_tag("ativar")
                        logger.info(f"Ativar: {bool(old_ativar)} ({old_ativar}) -> {bool(current_value)} ({current_value})")
                    else:
                        logger.error(f"Falha ao escrever na tag 'ativar'")
                
                # Processar novo valor para 'entregar'
                if args.new_entregar is not None:
                    old_entregar = handler.read_tag("entregar")
                    new_entregar = args.new_entregar.lower() in ["true", "t", "1", "yes", "y"]
                    result = handler.write_tag("entregar", new_entregar)
                    if result:
                        current_value = handler.read_tag("entregar")
                        logger.info(f"Entregar: {bool(old_entregar)} ({old_entregar}) -> {bool(current_value)} ({current_value})")
                    else:
                        logger.error(f"Falha ao escrever na tag 'entregar'")
                
                # Processar novo valor para 'gaveta'
                if args.new_gaveta is not None:
                    old_gaveta = handler.read_tag("gaveta")
                    result = handler.write_tag("gaveta", args.new_gaveta)
                    if result:
                        current_value = handler.read_tag("gaveta")
                        logger.info(f"Gaveta: {old_gaveta} -> {current_value}")
                    else:
                        logger.error(f"Falha ao escrever na tag 'gaveta'")
                
                # Processar novo valor para 'posicao_gaveta'
                if args.new_posicao_gaveta is not None:
                    old_posicao = handler.read_tag("posicao_gaveta")
                    result = handler.write_tag("posicao_gaveta", args.new_posicao_gaveta)
                    if result:
                        current_value = handler.read_tag("posicao_gaveta")
                        logger.info(f"Posicao_Gaveta: {old_posicao} -> {current_value}")
                    else:
                        logger.error(f"Falha ao escrever na tag 'posicao_gaveta'")
            
            # Ler e exibir valores atuais das tags
            logger.info("\n=== Valores atuais das tags ===")
            tags_to_read = ["ativar", "entregar", "gaveta", "posicao_gaveta"]
            tag_values = {}
            
            for tag in tags_to_read:
                value = handler.read_tag(tag)
                tag_values[tag] = value
                
                # Exibir informações detalhadas sobre cada tag
                if tag in ["ativar", "entregar"]:
                    logger.info(f"{tag.capitalize()} ({list(tags_to_read).index(tag)}): {bool(value)} ({value})")
                else:
                    logger.info(f"{tag.capitalize()} ({list(tags_to_read).index(tag)}): {value}")
            
            logger.info(f"Resumo das tags lidas: {tag_values}")
            
            # Desconectar
            client_manager.disconnect()
        else:
            logger.error("Falha ao conectar ao servidor Modbus")
    
    except Exception as e:
        logger.exception(f"Erro durante a execução: {e}")
    
    logger.info("Aplicação encerrada")

if __name__ == "__main__":
    write_values()
