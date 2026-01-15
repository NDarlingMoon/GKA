from pathlib import Path
from settings import Settings
import pytest
from pydantic import ValidationError

@pytest.fixture
def settings_instancia():
    """Cria uma instância da classe Settings com o config.yaml real."""
    return Settings()

# --- TESTES DE EXISTÊNCIA E ESTRUTURA ---
def test_config_file_exists():
    """Verifica se o arquivo físico config.yaml está no lugar certo."""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    assert config_path.exists(), f"O arquivo {config_path} deveria existir para os testes."

def test_invalid_config_raises_runtime_error():
    """O código lança RuntimeError quando o arquivo não existe."""
    with pytest.raises(RuntimeError) as excinfo:
        Settings(config_file='arquivo_fantasma.yaml')
    assert "Configuração inválida" in str(excinfo.value)

# --- TESTES DE INTEGRIDADE DE DADOS (FINANÇAS) ---
def test_paths_are_absolute_and_resolved(settings_instancia):
    """Garante que as properties resolvem o caminho."""
    path = settings_instancia.base_file
    assert path.is_absolute()
    assert isinstance(path, Path)

def test_colors_content(settings_instancia):
    """Garante que a UI não vai quebrar por falta de cores definidas."""
    assert isinstance(settings_instancia.colors, list)
    assert len(settings_instancia.colors) >= 1
    assert all(isinstance(c, str) for c in settings_instancia.colors)

def test_specific_files_properties(settings_instancia):
    """Verifica se as properties específicas estão mapeadas corretamente."""
    assert settings_instancia.cadastro_file.suffix in ['.xlsx', '.xls', '.xlsm']
    assert settings_instancia.gka_segmento_file.exists()

# --- TESTES DE VALIDAÇÃO DO PYDANTIC ---
def test_pydantic_validation_error(tmp_path):
    """Testa se o Pydantic bloqueia um YAML incompleto."""
    bad_config = tmp_path / "bad_config.yaml"
    bad_config.write_text("paths:\n  base: './base.xlsx'", encoding='utf-8')
    
    with pytest.raises(RuntimeError) as excinfo:
        Settings(config_file=str(bad_config))
    
    assert "Código Interrompido" in str(excinfo.value)