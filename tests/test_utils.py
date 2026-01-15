import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
import utils

# --- TESTES DE LEITURA (MOCKING) ---
def test_read_safe_excel_success():
    """Testa se a leitura retorna o DF quando o arquivo existe."""
    fake_path = Path("fake.xlsx")
    with patch("utils.validate_file", return_value=True), \
         patch("utils.pd.read_excel", return_value=pd.DataFrame({"col1": [1]})) as mock_read:
        
        df = utils.read_safe_excel(fake_path)
        
        assert isinstance(df, pd.DataFrame)
        assert "col1" in df.columns
        mock_read.assert_called_once()

def test_read_safe_excel_unsupported_engine():
    """Testa o comportamento quando a extensão não é catalogada."""
    with patch("utils.validate_file", return_value=True), \
         patch("utils.pd.read_excel") as mock_read:
        
        utils.read_safe_excel("arquivo.xyz")
        mock_read.assert_called_once()

def test_read_safe_excel_general_exception():
    """
    Testa se a função re-lança a exceção após emitir o aviso.
    """
    with patch("utils.validate_file", return_value=True), \
         patch("pandas.read_excel", side_effect=Exception("boom")):
        
        with pytest.raises(Exception) as excinfo:
            utils.read_safe_excel("fake.xlsx")
        
        assert "boom" in str(excinfo.value)

def test_invalid_config_raises_runtime_error():
    """Garante que o erro customizado de configuração é lançado."""
    with pytest.raises(RuntimeError) as excinfo:
        from settings import Settings
        Settings(config_file='fantasma.yaml')
    assert "Configuração inválida" in str(excinfo.value)

# --- TESTES DE TRANSFORMAÇÕES ---
@pytest.fixture
def df_exemplo():
    """Cria um DataFrame padrão para testar as limpezas."""
    return pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": ["  Varejo  ", "Atacado", " Varejo", "Outro", "Atacado"],
        "C": [10, 20, 30, 40, 50]
    })

def test_remove_lines_interval(df_exemplo):
    """Testa se a remoção por intervalo funciona (útil para cabeçalhos sujos)."""
    transform = utils.remove_lines(2, mode='interval')
    df_result = transform(df_exemplo)
    
    assert len(df_result) == 3
    assert df_result.iloc[0]["A"] == 3

def test_filter_columns_clean(df_exemplo):
    """Testa se o filtro remove espaços e seleciona corretamente (seu código usa .strip())."""
    transform = utils.filter_columns("B", "Varejo", "Atacado")
    df_result = transform(df_exemplo)
    
    assert len(df_result) == 4
    assert "Outro" not in df_result["B"].values

def test_rename_columns(df_exemplo):
    """Garante que a renomeação em massa funciona."""
    transform = utils.rename_columns("ID", "Segmento", "Valor")
    df_result = transform(df_exemplo)
    
    assert list(df_result.columns) == ["ID", "Segmento", "Valor"]