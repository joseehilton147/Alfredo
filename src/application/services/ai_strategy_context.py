"""Contexto para gerenciamento de estratégias de IA."""

import logging
from typing import Optional, Dict, Any, List
from enum import Enum

from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError, ProviderUnavailableError


class StrategyType(Enum):
    """Tipos de estratégias disponíveis."""
    WHISPER = "whisper"
    GROQ = "groq"
    OLLAMA = "ollama"


class AIStrategyContext:
    """Contexto para gerenciamento e troca dinâmica de estratégias de IA."""

    def __init__(self, strategies: Optional[Dict[str, AIStrategy]] = None, config: Optional[AlfredoConfig] = None):
        """Inicializa o contexto de estratégias.

        Args:
            strategies: Dicionário de estratégias disponíveis (injetadas)
            config: Configuração do Alfredo (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self._strategies: Dict[str, AIStrategy] = strategies or {}
        self._current_strategy: Optional[AIStrategy] = None
        self._initialize_default_strategy()

    def _initialize_default_strategy(self) -> None:
        """Inicializa a estratégia padrão."""
        if not self._strategies:
            self.logger.warning("Nenhuma estratégia foi injetada no contexto")
            return

        # Define estratégia padrão
        default_strategy = self.config.default_ai_provider
        if default_strategy in self._strategies:
            self._current_strategy = self._strategies[default_strategy]
            self.logger.info(f"Estratégia padrão definida: {default_strategy}")
        elif self._strategies:
            # Usa a primeira disponível como fallback
            first_available = next(iter(self._strategies.keys()))
            self._current_strategy = self._strategies[first_available]
            self.logger.info(f"Usando estratégia fallback: {first_available}")
        else:
            self.logger.error("Nenhuma estratégia de IA disponível")

    def register_strategy(self, name: str, strategy: AIStrategy) -> None:
        """Registra uma nova estratégia.

        Args:
            name: Nome da estratégia
            strategy: Instância da estratégia
        """
        if strategy.is_available():
            self._strategies[name] = strategy
            self.logger.info(f"Estratégia {name} registrada e disponível")
            
            # Se é a primeira estratégia ou é a padrão, define como atual
            if self._current_strategy is None or name == self.config.default_ai_provider:
                self._current_strategy = strategy
        else:
            self.logger.warning(f"Estratégia {name} não está disponível")

    def set_strategy(self, strategy_name: str) -> None:
        """Define a estratégia atual.

        Args:
            strategy_name: Nome da estratégia a ser usada

        Raises:
            ConfigurationError: Quando a estratégia não está disponível
        """
        if strategy_name not in self._strategies:
            available = list(self._strategies.keys())
            raise ConfigurationError(
                "ai_strategy",
                f"Estratégia '{strategy_name}' não está disponível",
                f"Estratégias disponíveis: {available}"
            )

        self._current_strategy = self._strategies[strategy_name]
        self.logger.info(f"Estratégia alterada para: {strategy_name}")

    def get_current_strategy(self) -> AIStrategy:
        """Retorna a estratégia atual.

        Returns:
            Estratégia de IA atual

        Raises:
            ProviderUnavailableError: Quando nenhuma estratégia está disponível
        """
        if self._current_strategy is None:
            raise ProviderUnavailableError(
                "ai_strategy",
                "Nenhuma estratégia de IA está disponível",
                details={"available_strategies": list(self._strategies.keys())}
            )

        return self._current_strategy

    def get_available_strategies(self) -> List[str]:
        """Retorna lista de estratégias disponíveis.

        Returns:
            Lista com nomes das estratégias disponíveis
        """
        return list(self._strategies.keys())

    def get_strategy_info(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """Retorna informações sobre uma estratégia.

        Args:
            strategy_name: Nome da estratégia (usa atual se não especificado)

        Returns:
            Dicionário com informações da estratégia

        Raises:
            ConfigurationError: Quando a estratégia não existe
        """
        if strategy_name is None:
            strategy = self.get_current_strategy()
        elif strategy_name in self._strategies:
            strategy = self._strategies[strategy_name]
        else:
            raise ConfigurationError(
                "ai_strategy",
                f"Estratégia '{strategy_name}' não encontrada"
            )

        return {
            "name": strategy.get_strategy_name(),
            "configuration": strategy.get_configuration(),
            "supported_languages": strategy.get_supported_languages(),
            "is_available": strategy.is_available()
        }

    def get_best_strategy_for_task(self, task: str) -> str:
        """Retorna a melhor estratégia para uma tarefa específica.

        Args:
            task: Tipo de tarefa ("transcription" ou "summarization")

        Returns:
            Nome da melhor estratégia para a tarefa

        Raises:
            ConfigurationError: Quando nenhuma estratégia suporta a tarefa
        """
        suitable_strategies = []

        for name, strategy in self._strategies.items():
            config = strategy.get_configuration()
            
            if task == "transcription":
                # Para transcrição, prefere estratégias que suportam transcrição
                if not config.get("transcription_only", True) or config.get("supports_transcription", True):
                    # Whisper e Groq são melhores para transcrição
                    if name in ["whisper", "groq"]:
                        suitable_strategies.append((name, 2))  # Alta prioridade
                    else:
                        suitable_strategies.append((name, 1))  # Baixa prioridade
                        
            elif task == "summarization":
                # Para sumarização, prefere estratégias com capacidade de LLM
                if config.get("supports_summarization", False):
                    if name in ["groq", "ollama"]:
                        suitable_strategies.append((name, 2))  # Alta prioridade
                    else:
                        suitable_strategies.append((name, 1))  # Baixa prioridade

        if not suitable_strategies:
            available = list(self._strategies.keys())
            raise ConfigurationError(
                "ai_strategy",
                f"Nenhuma estratégia disponível suporta a tarefa '{task}'",
                f"Estratégias disponíveis: {available}"
            )

        # Ordena por prioridade e retorna a melhor
        suitable_strategies.sort(key=lambda x: x[1], reverse=True)
        best_strategy = suitable_strategies[0][0]
        
        self.logger.info(f"Melhor estratégia para '{task}': {best_strategy}")
        return best_strategy

    async def transcribe_with_best_strategy(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcreve áudio usando a melhor estratégia disponível.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito
        """
        best_strategy_name = self.get_best_strategy_for_task("transcription")
        original_strategy = self._current_strategy
        
        try:
            self.set_strategy(best_strategy_name)
            return await self._current_strategy.transcribe(audio_path, language)
        finally:
            # Restaura estratégia original
            if original_strategy:
                self._current_strategy = original_strategy

    async def summarize_with_best_strategy(self, text: str, context: Optional[str] = None) -> str:
        """Sumariza texto usando a melhor estratégia disponível.

        Args:
            text: Texto para sumarizar
            context: Contexto adicional

        Returns:
            Resumo gerado
        """
        best_strategy_name = self.get_best_strategy_for_task("summarization")
        original_strategy = self._current_strategy
        
        try:
            self.set_strategy(best_strategy_name)
            return await self._current_strategy.summarize(text, context)
        finally:
            # Restaura estratégia original
            if original_strategy:
                self._current_strategy = original_strategy