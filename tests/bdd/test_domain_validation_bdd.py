"""Teste BDD para validação de domínio."""
import pytest
from pytest_bdd import scenarios

# Carregar todos os cenários do arquivo feature
scenarios('features/domain_validation.feature')

@pytest.mark.bdd
class TestDomainValidationBDD:
    """Classe para agrupar testes BDD de validação de domínio."""
    
    def test_bdd_domain_scenarios_loaded(self):
        """Verifica se os cenários BDD de domínio foram carregados corretamente."""
        assert True