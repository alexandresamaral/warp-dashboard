import pandas as pd
import csv
import os

def read_csv(file_path):
    """Lê o arquivo CSV e retorna um DataFrame."""
    df = pd.read_csv(file_path)
    return df

def create_status_list(df):
    """
    Cria uma lista de status únicos e ordenados a partir das colunas status_from_name e status_to_name.
    
    :param df: DataFrame contendo as colunas status_from_name e status_to_name.
    :return: Lista de status únicos e ordenados.
    """
    # Concatenar as colunas status_from_name e status_to_name, removendo valores nulos
    status_list = pd.concat([df['status_from_name'].dropna(), df['status_to_name'].dropna()])
    
    # Remover valores vazios e duplicados, e ordenar a lista
    status_list = sorted(set(status_list[status_list.notna()]))
    
    return status_list


def create_list(df):
    """
    Cria uma lista de status únicos e ordenados a partir das colunas status_from_name e status_to_name.
    
    :param df: DataFrame contendo as colunas status_from_name e status_to_name.
    :return: Lista de status únicos e ordenados.
    """
    # Concatenar as colunas status_from_name e status_to_name, removendo valores nulos
    status_list = pd.concat([df['status_name'].dropna(), df['status_name'].dropna()])
    
    # Remover valores vazios e duplicados, e ordenar a lista
    status_list = sorted(set(status_list[status_list.notna()]))
    
    return status_list


def save_to_csv(project_key, status_list, file_path):
    """Salva os dados em um arquivo CSV para um project_key, evitando duplicatas."""
    # Verificar se o arquivo existe
    file_exists = os.path.isfile(file_path)

    # Ler o arquivo CSV existente e armazenar as linhas em um conjunto
    existing_rows = set()
    if file_exists:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Pular o cabeçalho
            for row in reader:
                existing_rows.add(tuple(row))

    # Abrir o arquivo CSV no modo append para adicionar novas linhas
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escrever o cabeçalho apenas se o arquivo não existia anteriormente
        if not file_exists:
            writer.writerow(['project_key', 'status_name', 'wait_status'])
        
        for status in status_list:
            # Verificar se project_key ou status são nulos ou NaN
            if pd.notna(project_key) and pd.notna(status):
                new_row = (str(project_key), str(status), 'False')
                # Verificar novamente se algum elemento da new_row é nulo ou NaN
                if all(pd.notna(elem) for elem in new_row):
                    # Verificar se a linha já existe
                    if new_row not in existing_rows:
                        # Adicionar a nova linha ao conjunto e escrever no arquivo
                        existing_rows.add(new_row)
                        writer.writerow(new_row)


def fetch_from_csv(project_key, file_path):
    """Coleta os dados do arquivo CSV usando um project_key."""
    filtered_data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['project_key'] == project_key:
                filtered_data.append(row)
                
    return filtered_data

def update_csv(project_key, status_name, wait_status, file_path):
    """Atualiza os dados no arquivo CSV usando um project_key e status_name."""
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['project_key'] == project_key and row['status_name'] == status_name:
                row['wait_status'] = wait_status
            data.append(row)
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['project_key', 'status_name', 'wait_status'])
        writer.writeheader()
        writer.writerows(data)
    
    # print("Dados atualizados no arquivo CSV com sucesso.")

def delete_from_csv(project_key, file_path):
    """Exclui os dados do arquivo CSV usando um project_key."""
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['project_key'] != project_key:
                data.append(row)
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['project_key', 'status_name', 'wait_status'])
        writer.writeheader()
        writer.writerows(data)
    
    # print("Dados excluídos do arquivo CSV com sucesso.")


def compare_status(status_list, orginal_list):
    compare_list = []
    for status in status_list:
        if not status in orginal_list:
            compare_list.append(status)
    
    return compare_list

#########################################################################################


# Caminho do arquivo CSV original
csv_file_path = "original.csv"

# Leitura do arquivo CSV
df = read_csv(csv_file_path)

# Criação da lista de status únicos e ordenados
status_list_sorted = create_status_list(df)
# print("Lista de status únicos e ordenados:", status_list_sorted)

# Lista de project keys (substitua pelos valores reais)
project_key = "PRJ"

# Caminho do arquivo CSV para salvar os dados
csv_save_path = "workflow.csv"

# Salvamento em arquivo CSV
save_to_csv(project_key, status_list_sorted, csv_save_path)

# Coletar dados do arquivo CSV
fetched_data = fetch_from_csv(project_key, csv_save_path)
# print("Dados coletados do arquivo CSV:", fetched_data)

# Lista de status names para atualização (substitua pelos valores reais)
status_name = "Concluído"

# Atualizar dados no arquivo CSV
update_csv(project_key, status_name, True, csv_save_path)
# print("Dados atualizados no arquivo CSV.")

# Excluir dados do arquivo CSV
delete_from_csv(project_key, csv_save_path)
# print("Dados excluídos do arquivo CSV.")


def save_status_order(project_key, status_order, file_path):
    """Salva a ordem dos status para um projeto em um arquivo CSV."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['project_key', 'status_name'])
        for status in status_order:
            writer.writerow([project_key, status])

def load_status_order(project_key, file_path):
    """Carrega a ordem dos status para um projeto de um arquivo CSV."""
    if not os.path.exists(file_path):
        return None
    
    status_order = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['project_key'] == project_key:
                status_order.append(row['status_name'])
    
    return status_order if status_order else None
