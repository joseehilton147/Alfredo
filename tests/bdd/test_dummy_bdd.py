from pytest_bdd import scenarios

# Importa explicitamente os steps para garantir registro

# Steps dummy diretamente no arquivo de teste
from pytest_bdd import given, then

@given("dummy step")
def dummy_step():
    print("[DEBUG] Dummy step executado (inline)")

@then("dummy result")
def dummy_result():
    print("[DEBUG] Dummy result executado (inline)")

# Carrega o cenário dummy isolado
scenarios('features/dummy.feature')
