import os
import json
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union


def __init__(self, nome_arquivo: str = 'dados.json'):
    """
    Inicializa o gerenciador de arquivos
    
    Args:
        nome_arquivo (str): Nome do arquivo para manipulação
    """
    self.nome_arquivo = nome_arquivo
    self._criar_arquivo_se_nao_existir()

def _criar_arquivo_se_nao_existir(self):
    """Cria o arquivo se não existir"""
    if not os.path.exists(self.nome_arquivo):
        with open(self.nome_arquivo, 'w') as arquivo:
            json.dump([], arquivo)

def _validar_dados(self, dados: Dict[str, Any]) -> bool:
    """
    Valida se os dados não contêm valores nulos ou NaN
    
    Args:
        dados (Dict): Dicionário de dados a serem validados
    
    Returns:
        bool: True se dados são válidos, False caso contrário
    """
    for valor in dados.values():
        if valor is None or (isinstance(valor, float) and np.isnan(valor)):
            return False
    return True

def adicionar_registro(self, dados: Dict[str, Any]) -> bool:
    """
    Adiciona um novo registro ao arquivo
    
    Args:
        dados (Dict): Dicionário com os dados do registro
    
    Returns:
        bool: True se adicionado com sucesso, False caso contrário
    """
    if not self._validar_dados(dados):
        print("Erro: Dados inválidos. Não são permitidos valores nulos ou NaN.")
        return False

    try:
        with open(self.nome_arquivo, 'r+') as arquivo:
            registros = json.load(arquivo)
            
            # Gera um ID único
            dados['id'] = len(registros) + 1 if registros else 1
            
            registros.append(dados)
            
            arquivo.seek(0)
            json.dump(registros, arquivo, indent=4)
            arquivo.truncate()
        
        return True
    except Exception as e:
        print(f"Erro ao adicionar registro: {e}")
        return False

def ler_registros(self) -> List[Dict[str, Any]]:
    """
    Lê todos os registros do arquivo
    
    Returns:
        List: Lista de registros
    """
    try:
        with open(self.nome_arquivo, 'r') as arquivo:
            return json.load(arquivo)
    except Exception as e:
        print(f"Erro ao ler registros: {e}")
        return []

def atualizar_registro(self, id_registro: int, novos_dados: Dict[str, Any]) -> bool:
    """
    Atualiza um registro específico
    
    Args:
        id_registro (int): ID do registro a ser atualizado
        novos_dados (Dict): Novos dados para atualização
    
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    if not self._validar_dados(novos_dados):
        print("Erro: Dados inválidos. Não são permitidos valores nulos ou NaN.")
        return False

    try:
        with open(self.nome_arquivo, 'r+') as arquivo:
            registros = json.load(arquivo)
            
            for registro in registros:
                if registro['id'] == id_registro:
                    registro.update(novos_dados)
                    break
            
            arquivo.seek(0)
            json.dump(registros, arquivo, indent=4)
            arquivo.truncate()
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar registro: {e}")
        return False

def excluir_registro(self, id_registro: int) -> bool:
    """
    Exclui um registro específico
    
    Args:
        id_registro (int): ID do registro a ser excluído
    
    Returns:
        bool: True se excluído com sucesso, False caso contrário
    """
    try:
        with open(self.nome_arquivo, 'r+') as arquivo:
            registros = json.load(arquivo)
            
            registros = [reg for reg in registros if reg['id'] != id_registro]
            
            arquivo.seek(0)
            json.dump(registros, arquivo, indent=4)
            arquivo.truncate()
        
        return True
    except Exception as e:
        print(f"Erro ao excluir registro: {e}")
        return False

# Exemplo de uso
def main():
    # Inicializa o gerenciador de arquivos
    gerenciador = GerenciadorArquivos('usuarios.json')

    # Adicionar registro
    novo_usuario = {
        'nome': 'João Silva',
        'idade': 30,
        'email': 'joao@exemplo.com'
    }
    gerenciador.adicionar_registro(novo_usuario)

    # Ler registros
    registros = gerenciador.ler_registros()
    print("Registros:", registros)

    # Atualizar registro
    gerenciador.atualizar_registro(1, {'idade': 31})

    # Excluir registro
    gerenciador.excluir_registro(1)
