"""Testes de performance e benchmarks para Alfredo AI."""
import pytest
import time
import asyncio
import tempfile
import psutil
import threading
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any

from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.validators.video_validators import validate_video_id, validate_video_title
from src.domain.validators.url_validators import validate_url_format


# Função global para CPU-bound em testes de performance
def cpu_intensive_task(n: int) -> int:
    """Simula tarefa intensiva de CPU."""
    result = 0
    for i in range(n * 1000):
        result += i ** 2
    return result


class PerformanceTimer:
    """Utilitário para medir tempo de execução."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
    
    @property
    def elapsed(self) -> float:
        """Retorna tempo decorrido em segundos."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class MemoryProfiler:
    """Utilitário para monitorar uso de memória."""
    
    def __init__(self):
        self.initial_memory = None
        self.peak_memory = None
        self.final_memory = None
    
    def __enter__(self):
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        return self
    
    def __exit__(self, *args):
        self.final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = max(self.initial_memory, self.final_memory)
    
    @property
    def memory_increase(self) -> float:
        """Retorna aumento de memória em MB."""
        if self.initial_memory and self.final_memory:
            return self.final_memory - self.initial_memory
        return 0.0


@pytest.fixture
def performance_config():
    """Configuração otimizada para testes de performance."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = AlfredoConfig(
            base_dir=Path(temp_dir),
            data_dir=Path(temp_dir) / "data",
            temp_dir=Path(temp_dir) / "temp",
            max_video_duration=7200,  # 2 horas
            download_timeout=300,     # 5 minutos
            transcription_timeout=600, # 10 minutos
            max_concurrent_downloads=5
        )
        config.create_directory_structure()
        yield config


class TestValidationPerformance:
    """Testes de performance para validações."""
    
    @pytest.mark.performance
    def test_video_id_validation_performance(self):
        """Testa performance da validação de ID de vídeo."""
        test_ids = [
            f"video_id_{i:06d}" for i in range(10000)
        ]
        
        with PerformanceTimer() as timer:
            for video_id in test_ids:
                validate_video_id(video_id)
        
        # Deve processar 10k validações em menos de 1 segundo
        assert timer.elapsed < 1.0, f"Validação muito lenta: {timer.elapsed:.3f}s"
        
        # Performance por validação
        per_validation = timer.elapsed / len(test_ids) * 1000  # ms
        assert per_validation < 0.1, f"Validação individual muito lenta: {per_validation:.3f}ms"
    
    @pytest.mark.performance
    def test_video_title_validation_performance(self):
        """Testa performance da validação de título de vídeo."""
        test_titles = [
            f"Título de Vídeo Número {i:06d} - Teste de Performance" 
            for i in range(5000)
        ]
        
        with PerformanceTimer() as timer:
            for title in test_titles:
                validate_video_title(title)
        
        # Deve processar 5k validações em menos de 0.5 segundos
        assert timer.elapsed < 0.5, f"Validação de título muito lenta: {timer.elapsed:.3f}s"
    
    @pytest.mark.performance
    def test_url_validation_performance(self):
        """Testa performance da validação de URLs."""
        test_urls = [
            f"https://youtube.com/watch?v=video{i:06d}" 
            for i in range(1000)
        ]
        
        with PerformanceTimer() as timer:
            for url in test_urls:
                validate_url_format(url)
        
        # Deve processar 1k validações em menos de 0.2 segundos
        assert timer.elapsed < 0.2, f"Validação de URL muito lenta: {timer.elapsed:.3f}s"
    
    @pytest.mark.performance
    def test_video_entity_creation_performance(self):
        """Testa performance da criação de entidades Video."""
        video_data = [
            {
                "id": f"video_{i:06d}",
                "title": f"Vídeo de Performance {i}",
                "duration": 120.0 + (i % 100),
                "source_url": f"https://youtube.com/watch?v=perf{i:06d}"
            }
            for i in range(1000)
        ]
        
        with PerformanceTimer() as timer, MemoryProfiler() as memory:
            videos = []
            for data in video_data:
                video = Video(**data)
                videos.append(video)
        
        # Performance temporal
        assert timer.elapsed < 2.0, f"Criação de entidades muito lenta: {timer.elapsed:.3f}s"
        
        # Performance de memória (não deve usar mais que 50MB)
        assert memory.memory_increase < 50, f"Uso excessivo de memória: {memory.memory_increase:.1f}MB"
        
        # Verificar que todas as entidades foram criadas
        assert len(videos) == 1000


class TestConcurrencyPerformance:
    """Testes de performance para processamento concorrente."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_async_processing_performance(self):
        """Testa performance de processamento assíncrono."""
        async def mock_processing_task(task_id: int) -> str:
            """Simula tarefa de processamento assíncrona."""
            await asyncio.sleep(0.01)  # Simula I/O
            return f"result_{task_id}"
        
        num_tasks = 100
        
        # Teste sequencial
        with PerformanceTimer() as sequential_timer:
            sequential_results = []
            for i in range(num_tasks):
                result = await mock_processing_task(i)
                sequential_results.append(result)
        
        # Teste concorrente
        with PerformanceTimer() as concurrent_timer:
            tasks = [mock_processing_task(i) for i in range(num_tasks)]
            concurrent_results = await asyncio.gather(*tasks)
        
        # Processamento concorrente deve ser significativamente mais rápido
        speedup = sequential_timer.elapsed / concurrent_timer.elapsed
        assert speedup > 5, f"Speedup insuficiente: {speedup:.1f}x"
        
        # Resultados devem ser equivalentes
        assert len(concurrent_results) == len(sequential_results)
    
    @pytest.mark.performance
    def test_thread_pool_performance(self):
        """Testa performance de pool de processos usando função global."""
        tasks = [1000] * 20  # 20 tarefas

        # Teste sequencial
        with PerformanceTimer() as sequential_timer:
            sequential_results = [cpu_intensive_task(n) for n in tasks]

        # Teste com pool de processos (melhor para CPU-bound)
        with PerformanceTimer() as parallel_timer:
            with ProcessPoolExecutor(max_workers=4) as executor:
                parallel_results = list(executor.map(cpu_intensive_task, tasks))

        # Pool de processos deve ser mais rápido em sistemas multi-core
        speedup = sequential_timer.elapsed / parallel_timer.elapsed
        assert speedup > 1.2, f"Speedup insuficiente com pool de processos: {speedup:.1f}x"
        # Resultados devem ser idênticos
        assert sequential_results == parallel_results
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_semaphore_performance(self):
        """Testa performance de controle de concorrência com semáforo."""
        async def limited_task(task_id: int, semaphore: asyncio.Semaphore) -> str:
            async with semaphore:
                await asyncio.sleep(0.05)  # Simula operação limitada
                return f"limited_result_{task_id}"
        
        num_tasks = 50
        max_concurrent = 10
        semaphore = asyncio.Semaphore(max_concurrent)
        
        with PerformanceTimer() as timer:
            tasks = [limited_task(i, semaphore) for i in range(num_tasks)]
            results = await asyncio.gather(*tasks)
        
        # Deve completar em tempo razoável considerando o limite
        expected_min_time = (num_tasks / max_concurrent) * 0.05
        assert timer.elapsed >= expected_min_time * 0.8  # 80% do tempo mínimo teórico
        assert timer.elapsed <= expected_min_time * 2.0  # Máximo 2x o tempo teórico
        
        assert len(results) == num_tasks


class TestMemoryPerformance:
    """Testes de performance de memória."""
    
    @pytest.mark.performance
    def test_large_dataset_memory_usage(self):
        """Testa uso de memória com grandes volumes de dados."""
        with MemoryProfiler() as memory:
            # Simular processamento de grande volume de vídeos
            videos = []
            for i in range(10000):
                video = Video(
                    id=f"memory_test_{i:06d}",
                    title=f"Memory Test Video {i}",
                    duration=float(120 + (i % 1000)),
                    source_url=f"https://youtube.com/watch?v=mem{i:06d}"
                )
                videos.append(video)
                
                # Limpar periodicamente para simular processamento em lotes
                if i % 1000 == 999:
                    # Simular processamento e limpeza
                    processed_count = len(videos)
                    videos.clear()
        
        # Uso de memória não deve exceder 100MB
        assert memory.memory_increase < 100, f"Uso excessivo de memória: {memory.memory_increase:.1f}MB"
    
    @pytest.mark.performance
    def test_memory_leak_detection(self):
        """Testa detecção de vazamentos de memória."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Executar múltiplos ciclos de criação/destruição
        for cycle in range(10):
            videos = []
            for i in range(1000):
                video = Video(
                    id=f"leak_test_{cycle}_{i:04d}",
                    title=f"Leak Test Video {cycle}-{i}",
                    duration=120.0,
                    source_url=f"https://youtube.com/watch?v=leak{cycle}{i:04d}"
                )
                videos.append(video)
            
            # Limpar explicitamente
            del videos
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Aumento de memória deve ser mínimo (< 10MB)
        assert memory_increase < 10, f"Possível vazamento de memória: {memory_increase:.1f}MB"


class TestTimeoutPerformance:
    """Testes de performance para timeouts e limites."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_timeout_enforcement(self, performance_config):
        """Testa enforcement de timeouts."""
        timeout = 0.1  # 100ms
        
        async def slow_operation():
            await asyncio.sleep(0.2)  # 200ms - deve dar timeout
            return "never_reached"
        
        with PerformanceTimer() as timer:
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(slow_operation(), timeout=timeout)
        
        # Timeout deve ser respeitado com margem de erro mínima
        assert timer.elapsed < timeout * 1.5, f"Timeout não respeitado: {timer.elapsed:.3f}s"
    
    @pytest.mark.performance
    def test_configuration_validation_performance(self, performance_config):
        """Testa performance da validação de configuração."""
        configs = []
        
        with PerformanceTimer() as timer:
            for i in range(1000):
                config = AlfredoConfig(
                    max_video_duration=3600 + i,
                    download_timeout=300 + (i % 100),
                    transcription_timeout=600 + (i % 200)
                )
                configs.append(config)
        
        # Criação de 1000 configurações deve ser rápida
        assert timer.elapsed < 1.0, f"Validação de config muito lenta: {timer.elapsed:.3f}s"
        
        # Testar validação runtime
        with PerformanceTimer() as runtime_timer:
            for config in configs[:100]:  # Testar subset
                config.validate_runtime()
        
        assert runtime_timer.elapsed < 0.1, f"Validação runtime muito lenta: {runtime_timer.elapsed:.3f}s"


class TestScalabilityPerformance:
    """Testes de performance de escalabilidade."""
    
    @pytest.mark.performance
    def test_linear_scaling_performance(self):
        """Testa se performance escala linearmente com o volume."""
        def process_batch(size: int) -> float:
            """Processa lote de vídeos e retorna tempo."""
            with PerformanceTimer() as timer:
                videos = []
                for i in range(size):
                    video = Video(
                        id=f"scale_test_{i:06d}",
                        title=f"Scale Test Video {i}",
                        duration=120.0,
                        source_url=f"https://youtube.com/watch?v=scale{i:06d}"
                    )
                    videos.append(video)
            return timer.elapsed
        
        # Testar diferentes tamanhos de lote
        batch_sizes = [100, 500, 1000, 2000]
        times = []
        
        for size in batch_sizes:
            time_taken = process_batch(size)
            times.append(time_taken)
        
        # Verificar escalabilidade aproximadamente linear
        # Tempo para 2000 não deve ser mais que 25x o tempo para 100
        ratio = times[-1] / times[0]  # 2000 vs 100
        expected_ratio = batch_sizes[-1] / batch_sizes[0]  # 20x
        
        assert ratio < expected_ratio * 1.5, f"Escalabilidade ruim: {ratio:.1f}x vs esperado {expected_ratio}x"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_limit_performance(self, performance_config):
        """Testa performance com limites de concorrência."""
        max_concurrent = performance_config.max_concurrent_downloads
        
        async def mock_download(download_id: int) -> str:
            await asyncio.sleep(0.1)  # Simula download
            return f"download_{download_id}"
        
        # Testar com número de downloads igual ao limite
        with PerformanceTimer() as at_limit_timer:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def limited_download(download_id: int) -> str:
                async with semaphore:
                    return await mock_download(download_id)
            
            tasks = [limited_download(i) for i in range(max_concurrent)]
            results = await asyncio.gather(*tasks)
        
        # Testar com número de downloads acima do limite
        with PerformanceTimer() as above_limit_timer:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def limited_download(download_id: int) -> str:
                async with semaphore:
                    return await mock_download(download_id)
            
            tasks = [limited_download(i) for i in range(max_concurrent * 2)]
            results = await asyncio.gather(*tasks)
        
        # Tempo com limite duplo deve ser aproximadamente o dobro
        ratio = above_limit_timer.elapsed / at_limit_timer.elapsed
        assert 1.8 <= ratio <= 2.5, f"Controle de concorrência ineficiente: {ratio:.1f}x"
        
        assert len(results) == max_concurrent * 2


@pytest.mark.performance
class TestBenchmarkSuite:
    """Suite de benchmarks para comparação de performance."""
    
    def test_comprehensive_benchmark(self, performance_config):
        """Benchmark abrangente do sistema."""
        benchmark_results = {}
        
        # Benchmark 1: Validação
        with PerformanceTimer() as timer:
            for i in range(10000):
                validate_video_id(f"benchmark_video_{i:06d}")
        benchmark_results["validation_10k"] = timer.elapsed
        
        # Benchmark 2: Criação de entidades
        with PerformanceTimer() as timer:
            videos = []
            for i in range(5000):
                video = Video(
                    id=f"benchmark_{i:06d}",
                    title=f"Benchmark Video {i}",
                    duration=120.0,
                    source_url=f"https://youtube.com/watch?v=bench{i:06d}"
                )
                videos.append(video)
        benchmark_results["entity_creation_5k"] = timer.elapsed
        
        # Benchmark 3: Configuração
        with PerformanceTimer() as timer:
            configs = []
            for i in range(1000):
                config = AlfredoConfig(
                    max_video_duration=3600,
                    download_timeout=300,
                    transcription_timeout=600
                )
                configs.append(config)
        benchmark_results["config_creation_1k"] = timer.elapsed
        
        # Imprimir resultados para referência
        print("\n=== BENCHMARK RESULTS ===")
        for test_name, elapsed_time in benchmark_results.items():
            print(f"{test_name}: {elapsed_time:.3f}s")
        
        # Verificar que todos os benchmarks completaram em tempo razoável
        assert all(time < 10.0 for time in benchmark_results.values()), \
            "Algum benchmark excedeu 10 segundos"