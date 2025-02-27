#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para configuração de logging da aplicação.
"""

import logging
import logging.handlers
import os
import sys

# Importação relativa para evitar problemas de importação circular
from src.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT

def setup_logging():
    """
    Configura o sistema de logging da aplicação.
    
    Configura handlers para console e arquivo, com rotação de arquivos
    quando o tamanho máximo é atingido.
    """
    # Criar o diretório de logs se não existir
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Obter o nível de log a partir da configuração
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configurar o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Criar formatador
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Configurar handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configurar handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Configurar logging para bibliotecas externas
    logging.getLogger('pymodbus').setLevel(logging.WARNING)
    
    logging.info("Sistema de logging configurado")
    return root_logger
