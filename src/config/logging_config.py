"""
Configuração centralizada de logging estruturado para o Alfredo AI.
Inclui suporte a formato JSON, níveis de log e proteção de dados sensíveis.
"""
import logging
import json
from logging import LogRecord
from typing import Any, Dict

class SensitiveDataFilter(logging.Filter):
    """Filtro para remover dados sensíveis dos logs."""
    SENSITIVE_KEYS = {"api_key", "token", "password", "secret"}

    def filter(self, record: LogRecord) -> bool:
        if hasattr(record, "msg") and isinstance(record.msg, dict):
            for key in self.SENSITIVE_KEYS:
                if key in record.msg:
                    record.msg[key] = "***"
        return True

class JsonFormatter(logging.Formatter):
    """Formata logs como JSON estruturado."""
    def format(self, record: LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

def setup_structured_logging(log_file: str, level: int = logging.INFO, to_stdout: bool = True) -> None:
    """
    Configura logging estruturado (JSON) para o Alfredo AI.
    Inclui filtro de dados sensíveis e handlers para arquivo e console.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = JsonFormatter()
    sensitive_filter = SensitiveDataFilter()

    # Handler para arquivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(sensitive_filter)
    logger.addHandler(file_handler)

    # Handler para stdout (opcional)
    if to_stdout:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(sensitive_filter)
        logger.addHandler(stream_handler)

    # Evita duplicidade de logs
    logger.propagate = False
