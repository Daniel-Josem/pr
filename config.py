"""
Configuración para el sistema de manejo de errores
"""
import os
from datetime import timedelta

class ErrorConfig:
    """Configuración para el manejo de errores"""
    
    # Configuración de logging
    LOG_DIRECTORY = os.path.join(os.path.dirname(__file__), 'logs')
    LOG_FILE_NAME = 'error.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = 'ERROR'
    
    # Configuración de rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = 100  # requests por hora
    RATE_LIMIT_WINDOW = 3600  # 1 hora en segundos
    
    # IPs exentas de rate limiting (para desarrollo)
    RATE_LIMIT_EXEMPT_IPS = ['127.0.0.1', 'localhost']
    
    # Configuración de seguridad
    SECURITY_ENABLED = True
    BLOCK_SUSPICIOUS_REQUESTS = True
    
    # Patrones sospechosos para bloquear
    SUSPICIOUS_PATTERNS = [
        '../', '..\\', '/etc/', '/proc/', '/sys/',
        'SELECT', 'INSERT', 'DELETE', 'UPDATE', 'DROP',
        '<script>', '</script>', 'javascript:', 'vbscript:',
        'onload=', 'onerror=', 'onclick=', 'eval(', 'exec(',
        'cmd.exe', 'powershell', '/bin/sh', '/bin/bash'
    ]
    
    # User agents sospechosos
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap', 'nikto', 'dirb', 'gobuster', 'wpscan',
        'nmap', 'masscan', 'zap', 'burp', 'crawler'
    ]
    
    # Configuración de monitoreo
    MONITORING_ENABLED = True
    HEALTH_CHECK_ENABLED = True
    ERROR_STATS_ENABLED = True
    
    # Configuración de notificaciones (futuro)
    NOTIFICATION_EMAIL = None
    NOTIFICATION_WEBHOOK = None
    
    # Configuración de limpieza de logs
    AUTO_CLEANUP_LOGS = True
    LOG_RETENTION_DAYS = 30
    
    # Configuración de cache para errores
    CACHE_ERROR_RESPONSES = True
    CACHE_TIMEOUT = 300  # 5 minutos

class DevelopmentErrorConfig(ErrorConfig):
    """Configuración para desarrollo"""
    LOG_LEVEL = 'DEBUG'
    RATE_LIMIT_ENABLED = False
    SECURITY_ENABLED = False
    CACHE_ERROR_RESPONSES = False

class ProductionErrorConfig(ErrorConfig):
    """Configuración para producción"""
    LOG_LEVEL = 'ERROR'
    RATE_LIMIT_ENABLED = True
    SECURITY_ENABLED = True
    CACHE_ERROR_RESPONSES = True
    RATE_LIMIT_DEFAULT = 60  # Más restrictivo en producción

# Configuración por defecto
DEFAULT_CONFIG = DevelopmentErrorConfig
