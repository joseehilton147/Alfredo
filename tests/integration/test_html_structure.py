"""
Testa estrutura, responsividade e acessibilidade do HTML gerado pelo Alfredo AI.
"""
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

@pytest.mark.integration
@pytest.mark.parametrize("html_path", [
    # Adapte o caminho conforme necessário para o ambiente de teste real
    "data/output/youtube_e2e_test.html",
    "data/output/local_e2e_test.html"
])
def test_html_structure_and_responsiveness(html_path):
    html_file = Path(html_path)
    if not html_file.exists():
        pytest.skip(f"Arquivo HTML não encontrado: {html_path}")
    content = html_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")

    # Estrutura básica
    assert soup.html is not None
    assert soup.head is not None
    assert soup.body is not None
    assert soup.title is not None
    assert soup.find("meta", attrs={"charset": "utf-8"}) is not None
    assert soup.find("meta", attrs={"name": "viewport"}) is not None

    # Responsividade e classes
    style = soup.find("style")
    assert style is not None and "@media" in style.text
    assert soup.find(class_="transcription") is not None
    # Acessibilidade mínima: título e contraste
    assert soup.h1 is not None
    assert "Alfredo AI" in soup.text
