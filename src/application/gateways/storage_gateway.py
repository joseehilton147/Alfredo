"""
Gateway para armazenamento de dados.

Este módulo define a interface abstrata para persistência de dados do sistema,
seguindo os princípios da Clean Architecture onde a camada de aplicação define
contratos que a infraestrutura deve implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

from src.domain.entities.video import Video


class StorageGateway(ABC):
    """
    Interface abstrata para armazenamento de dados.
    
    Esta interface define os contratos que implementações concretas de storage
    devem seguir, permitindo isolamento da infraestrutura e facilitando
    testes através de mocks.
    """

    @abstractmethod
    async def save_video(self, video: Video) -> None:
        """
        Salva os metadados de um vídeo.
        
        Args:
            video: Entidade Video com todos os metadados
            
        Raises:
            ConfigurationError: Quando há problemas de configuração de storage
            AlfredoError: Quando ocorre erro genérico de persistência
        """
        pass

    @abstractmethod
    async def load_video(self, video_id: str) -> Optional[Video]:
        """
        Carrega um vídeo pelo seu ID.
        
        Args:
            video_id: ID único do vídeo
            
        Returns:
            Optional[Video]: Entidade Video ou None se não encontrado
            
        Raises:
            ConfigurationError: Quando há problemas de configuração de storage
            AlfredoError: Quando ocorre erro genérico de leitura
        """
        pass

    @abstractmethod
    async def save_transcription(
        self, 
        video_id: str, 
        transcription: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Salva a transcrição de um vídeo com metadados opcionais.
        
        Args:
            video_id: ID do vídeo associado à transcrição
            transcription: Texto da transcrição
            metadata: Metadados adicionais como:
                - language: Idioma da transcrição
                - provider: Provedor de IA usado
                - model: Modelo específico usado
                - confidence: Nível de confiança
                - processing_time: Tempo de processamento
                - created_at: Timestamp da criação
                
        Raises:
            InvalidVideoFormatError: Quando video_id não é válido
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de persistência
        """
        pass

    @abstractmethod
    async def load_transcription(self, video_id: str) -> Optional[str]:
        """
        Carrega a transcrição de um vídeo pelo ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Optional[str]: Texto da transcrição ou None se não encontrada
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de leitura
        """
        pass

    @abstractmethod
    async def save_summary(
        self,
        video_id: str,
        summary: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Salva o resumo de um vídeo com metadados opcionais.
        
        Args:
            video_id: ID do vídeo associado ao resumo
            summary: Texto do resumo
            metadata: Metadados adicionais como:
                - provider: Provedor de IA usado
                - model: Modelo específico usado
                - summary_type: Tipo de resumo (bullet_points, paragraph, etc.)
                - processing_time: Tempo de processamento
                - created_at: Timestamp da criação
                
        Raises:
            InvalidVideoFormatError: Quando video_id não é válido
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de persistência
        """
        pass

    @abstractmethod
    async def load_summary(self, video_id: str) -> Optional[str]:
        """
        Carrega o resumo de um vídeo pelo ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Optional[str]: Texto do resumo ou None se não encontrado
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de leitura
        """
        pass

    @abstractmethod
    async def list_videos(
        self, 
        limit: int = 100, 
        offset: int = 0,
        filter_by: Optional[Dict] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Video]:
        """
        Lista vídeos com suporte a paginação e filtros.
        
        Args:
            limit: Número máximo de vídeos a retornar
            offset: Número de vídeos a pular (para paginação)
            filter_by: Filtros opcionais:
                - has_transcription: bool - Apenas vídeos com/sem transcrição
                - has_summary: bool - Apenas vídeos com/sem resumo
                - source_type: str - "local" ou "remote"
                - date_from: datetime - Vídeos criados após esta data
                - date_to: datetime - Vídeos criados antes desta data
            sort_by: Campo para ordenação ("created_at", "title", "duration")
            sort_order: Ordem de classificação ("asc" ou "desc")
            
        Returns:
            List[Video]: Lista de vídeos que atendem aos critérios
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            InvalidVideoFormatError: Quando parâmetros são inválidos
            AlfredoError: Quando ocorre erro genérico de leitura
        """
        pass

    @abstractmethod
    async def delete_video(self, video_id: str) -> bool:
        """
        Remove um vídeo e todos os dados associados.
        
        Args:
            video_id: ID do vídeo a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de remoção
        """
        pass

    @abstractmethod
    async def video_exists(self, video_id: str) -> bool:
        """
        Verifica se um vídeo existe no storage.
        
        Args:
            video_id: ID do vídeo a ser verificado
            
        Returns:
            bool: True se existe, False caso contrário
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
        """
        pass

    @abstractmethod
    async def get_storage_stats(self) -> Dict:
        """
        Obtém estatísticas do storage.
        
        Returns:
            Dict: Estatísticas contendo:
                - total_videos: int - Total de vídeos armazenados
                - videos_with_transcription: int - Vídeos com transcrição
                - videos_with_summary: int - Vídeos com resumo
                - total_storage_size: int - Tamanho total em bytes
                - oldest_video: datetime - Data do vídeo mais antigo
                - newest_video: datetime - Data do vídeo mais recente
                
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de leitura
        """
        pass

    @abstractmethod
    async def cleanup_orphaned_data(self) -> int:
        """
        Remove dados órfãos (transcrições/resumos sem vídeo associado).
        
        Returns:
            int: Número de registros órfãos removidos
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de limpeza
        """
        pass

    @abstractmethod
    async def backup_data(self, backup_path: str) -> bool:
        """
        Cria backup de todos os dados.
        
        Args:
            backup_path: Caminho onde o backup será salvo
            
        Returns:
            bool: True se backup criado com sucesso
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            AlfredoError: Quando ocorre erro genérico de backup
        """
        pass

    @abstractmethod
    async def restore_data(self, backup_path: str) -> bool:
        """
        Restaura dados de um backup.
        
        Args:
            backup_path: Caminho do arquivo de backup
            
        Returns:
            bool: True se restaurado com sucesso
            
        Raises:
            ConfigurationError: Quando há problemas de configuração
            InvalidVideoFormatError: Quando backup é inválido
            AlfredoError: Quando ocorre erro genérico de restauração
        """
        pass