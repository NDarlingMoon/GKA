from datetime import datetime
import pandas as pd
import os
from pathlib import Path
import warnings
from typing import Callable

def current_ano_safra(month=None) -> str:
    """
    Verifica e retorna o Ano-Safra atual.

    A regra aplicada é:
    - Abril (4): retorna "1"
    - Maio em diante (>= 5): retorna mês - 3
    - Janeiro a Março (< 4): retorna mês + 9

    Args:
        month (int, optional): O mês civil a ser convertido. 
            Se None, utiliza o mês atual do sistema.    

    Returns:
        str: Retorna um número em formato String.

    Raises:
        ValueError: Retorna ValueError caso o mês esteja acima de 12 ou abaixo de 1.

    Example:
        >>> current_ano_safra()
        "4"
        >>> current_ano_safra(9)
        "6"
    """
    if month is None:
        month = datetime.now().month

    if not 1<= month <= 12:
        raise ValueError("O parâmetro 'month' deve estar entre 1 e 12.")

    if month == 4:
        return str(1)
    elif month >= 5:
        return str(month - 3)
    else:
        return str(month + 9)

def validate_file(path) -> True:
    """
    Verifica se o arquivo existe e é acessível.
    Esta função atua como um guardião antes do carregamento de dados pesados,
    garantindo que o caminho é válido e acessível.

    Args:
        path (str or Path): O caminho do arquivo.

    Returns:
        True: True se o arquivo existir e for legível.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado, retorna FileNotFoundError.
        PermissionError: Caso não haja permissão para abrir o arquivo, retorna PermissionError.
        
    Example:
        >>> validate_file("data/input.csv")
        True
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {p.absolute()}")
    if not os.access(p, os.R_OK):
        raise PermissionError(f"Sem permissão de leitura no arquivo: {p}")
    return True

def read_safe_excel(path, **kwargs) -> pd.DataFrame:
    """
    Tenta ler um arquivo Excel tratando extensões e motores automaticamente.
    Args:
        path (str or Path): O caminho do arquivo.
        *kwargs: Argumentos adicionais repassados para pandas.read_excel.

    Returns:
        pd.DataFrame: Retorna um DataFrame Pandas.

        
    Example:
        >>> read_safe_excel("data/input.xlsx", sheet_name="Sheet1")
    """
    validate_file(path)

    p = Path(path)
    ext = p.suffix.lower()

    engines = {
        '.xlsx': 'openpyxl',
        '.xlsm': 'openpyxl',
        '.xls':  'xlrd',
        '.xlsb': 'pyxlsb'
    }

    try:
        if ext in engines and 'engine' not in kwargs:
            kwargs['engine'] = engines[ext]
        else:
            if 'engine' not in kwargs:
                warnings.warn(f"ℹExtensão {ext} não catalogada. Tentando motor padrão do Pandas.", UserWarning)
        return pd.read_excel(p, **kwargs)

    except ImportError as e:
        needed_pkg = engines.get(ext, "o motor adequado")
        warnings.warn(f"Erro: Falta instalar o pacote para arquivos {ext}. Tente: pip install {needed_pkg}", UserWarning)
        raise
    except Exception as e:
        warnings.warn(f"Erro ao ler {p.name}: {e}", UserWarning)
        raise

def remove_lines(*args, mode='individual'):
    """
    Remove linhas de um DataFrame.
    Args:
        *args (int): Recebe quais linhas devem ser removidas.
        mode: Diz se as linhas devem ser removidas de forma individual ou em intervalo.
            'individual' (padrão): Removerá exatamente as linhas informadas.
            'interval': Removerá uma faixa de linhas baseado nas informadas.

    Returns:
        pd.DataFrame: Retorna um DataFrame Pandas.

        
    Example:
        >>> remove_lines(1, 4, 6, 9 ,8)
        >>> remove_lines(2, 6, mode='interval')
        >>> remove_lines(7)
    """
    def transform_df(df):
        if mode == 'interval' and len(args) == 1:
            return df.drop(list(range(0, args[0])))
        elif mode == 'interval' and len(args) == 2:
            return df.drop(list(range(args[0],args[1])))
        else:
            return df.drop(list(args))
    return transform_df

def remove_columns(*args, mode='individual'):
    """
    Remove colunas de um DataFrame.
    Args:
        *args (int): Recebe quais colunas devem ser removidas.
        mode: Diz se as colunas devem ser removidas de forma individual ou em intervalo.
            'individual' (padrão): Removerá exatamente as colunas informadas.
            'interval': Removerá uma faixa de colunas baseado nas informadas.

    Returns:
        pd.DataFrame: Retorna um DataFrame Pandas.

        
    Example:
        >>> remove_columns(1, 4, 6, 9 ,8)
        >>> remove_columns(2, 6, mode='interval')
        >>> remove_columns(7)
    """
    def transform_df(df):
        if mode == 'interval' and len(args) == 1:
            return df.drop(df.columns[0:args[0]], axis=1)
        elif mode == 'interval' and len(args) == 2:
            return df.drop(df.columns[args[0]:args[1]], axis=1)
        else:
            return df.drop(df.columns[list(args)], axis=1)
    return transform_df

def rename_columns(*args):
    """Renomeia colunas de um DataFrame."""
    def transform_df(df):
        return df.set_axis(list(args), axis=1)
    return transform_df

def filter_columns(column, *args):
    """Filtra colunas de um DataFrame."""
    def transform_df(df):
        values = args[0] if len(args) == 1 and isinstance(args[0], (list, pd.Series, set)) else args
        return df[df[column].str.strip().isin(values)].copy()
    return transform_df

def extract_column(column, mode='not-in', *args):
    """
    Extrai valores únicos de uma coluna após limpar a estrutura do DataFrame.

    A função realiza a remoção de colunas duplicadas, limpa espaços em branco 
    nos nomes das colunas e nos dados, e permite filtrar o resultado final.

    Args:
        column (str): O nome da coluna a ser extraída.
        mode (str, optional): O modo de filtragem. 
            'not-in' (padrão): Retorna todos os valores EXCETO os passados em *args.
            'in': Retorna APENAS os valores que estiverem presentes em *args.
        *args: Valores de referência para o filtro. Podem ser strings, números 
            ou uma lista expandida de termos (ex: "A CLASSIFICAR", "N/A").

    Returns:
        list: Uma lista de strings com os valores únicos e limpos.

    Raises:
        KeyError: Se a coluna especificada não existir no DataFrame.
        
    Example:
        >>> kams = df.pipe(extract_column("KAM", "not-in", "A CLASSIFICAR"))
        >>> skus = df.pipe(extract_column("Status", "in", "ATIVO", "PENDENTE"))
    """
    def transform_column(df):
        df = df.loc[:, ~df.columns.duplicated()].copy()
        df.columns = [str(c).strip() for c in df.columns]

        if column not in df.columns:
            raise KeyError(f"Coluna '{column}' não encontrada. Colunas disponíveis: {list(df.columns)}")

        unique_values = (
            df.loc[:, column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )
        if mode == 'not-in':
            column_list = [t for t in unique_values if t not in args]
        elif mode == "in":
            column_list = [t for t in unique_values if t in args]         
        else:
            raise ValueError("O valor do segundo parâmetro deve ser 'in' ou 'not-in'.")   
        
        return column_list
    return transform_column

def clean_key(col: str | list) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """
    Normaliza um DataFrame para que seja possível trabalhar com ele.
    Passa o texto para letras maiúsculas, remove espaços em branco e garante o tipo String.
    Args:
        col (str): Nome da coluna a ser normalizada.

    Returns:
        pd.DataFrame: Retorna o DataFrame com a coluna normalizada.

    Raises:
        KeyError: Se a coluna não for encontrada, retorna KeyError.
        
    Example:
        >>> kams = df.pipe(clean_key("IBM DODO"))
    """
    column_list = [col] if isinstance(col, str) else col

    def transform_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in column_list:
            if col not in df.columns:
                raise KeyError(f"Coluna '{col}' não encontrada.")

            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].replace('NAN', pd.NA).replace('NONE', pd.NA)
            
        return df
    return transform_df