import yaml
from pathlib import Path
from pydantic import BaseModel, FilePath, ValidationError, DirectoryPath
from rich.console import Console

console = Console()

def join_constructor(loader, node):
    """Construtor YAML para concatenar strings (usado para montar caminhos)."""
    seq = loader.construct_sequence(node)
    return "".join([str(i) for i in seq])

yaml.add_constructor('!join', join_constructor)

class PathConfig(BaseModel):
    """
    Schema de validação de caminhos. 
    O tipo FilePath garante que o arquivo EXISTA no disco.
    """
    base: FilePath
    cadastro: FilePath
    gka_por_segmento: FilePath
    lista_gka: FilePath
    portfolio: FilePath
    oem: FilePath
    sellin: FilePath
    output_path: DirectoryPath

class Settings:
    def __init__(self, config_file='config.yaml'):
        config_path = Path(__file__).parent / config_file

        if not config_path.exists():
            console.print(f"[bold red]ERRO:[/bold red] Configuração não encontrada em {config_path}")
            raise RuntimeError("Configuração inválida")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                raw_data = yaml.load(file, Loader=yaml.FullLoader)
            
            self._paths = PathConfig(**raw_data.get('paths', {}))
            self._colors = raw_data.get('ui', {}).get('colors', [])
            self._outputs = raw_data.get('outputs', {}).get('file_name', [])
            
            console.print("[bold green]:white_check_mark: Configurações e arquivos validados com sucesso![/bold green]")

        except ValidationError as e:
            console.print("\n[bold yellow]:warning: Falha na integridade dos dados/caminhos:[/bold yellow]")
            for error in e.errors():
                campo = error['loc'][0]
                msg = "Arquivo não encontrado no diretório especificado." if "file_path" in error['type'] else error['msg']
                console.print(f"  • [cyan]{campo}[/cyan]: {msg}")
            
            console.print("\n[bold red]Interrompendo Script.[/bold red]")
            raise RuntimeError("Código Interrompido")
            
        except Exception as e:
            console.print(f"[bold red]ERRO INESPERADO AO LER YAML:[/bold red] {e}")
            raise RuntimeError("Erro Inesperado")

    @property
    def base_file(self) -> Path:
        return self._paths.base.resolve()

    @property
    def cadastro_file(self) -> Path:
        return self._paths.cadastro.resolve()

    @property
    def gka_segmento_file(self) -> Path:
        return self._paths.gka_por_segmento.resolve()

    @property
    def lista_gka_file(self) -> Path:
        return self._paths.lista_gka.resolve()

    @property
    def portfolio_file(self) -> Path:
        return self._paths.portfolio.resolve()
    
    
    @property
    def oem_file(self) -> Path:
        return self._paths.oem.resolve()
    
    
    @property
    def sellin_file(self) -> Path:
        return self._paths.sellin.resolve()
    
    @property
    def output_path(self) -> Path:
        return self._paths.output_path.resolve()

    @property
    def file_name(self):
        return self._outputs

    @property
    def colors(self):
        return self._colors