import zipfile
import requests
from bs4 import BeautifulSoup
import os
import tabula
import pandas as pd

# Pega Url, faz uma requisição e verifica.
url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'

response = requests.get(url)

if response.status_code == 200:
    print("Requisição bem-sucedida!")

# Analisar o conteúdo HTML da página
soup = BeautifulSoup(response.content, 'html.parser')

# Procurar links e filtra PDFs dos Anexos I e II e pega apenas .pdf
links = []

for link in soup.find_all('a', href=True):
    href = link['href']
    if ('anexo i' in link.text.lower() or 'anexo ii' in link.text.lower()):
        if href.lower().endswith('.pdf'):
            if not href.startswith('http'):
                href = 'https://www.gov.br' + href
            links.append(href)

# Exibe os links
if links:
    print("Links encontrados:")
    for pdf in links:
        print(pdf)

# Download dos pdfs


def download_pdf(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Download bem-sucedido: {save_path}")
    else:
        print(
            f"Falha no download de {url}, código de status: {response.status_code}")


# Cria uma pasta e adiciona os pdfs instalados nela.
os.makedirs('pdfs', exist_ok=True)

for i, pdf_url in enumerate(links):
    pdf_name = f'pdfs/anexo_{i+1}.pdf'
    download_pdf(pdf_url, pdf_name)

# zipa os pdfs.


def zip_pdfs(pdf_folder, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(pdf_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(
                    os.path.join(root, file), pdf_folder))


zip_pdfs('pdfs', 'anexos.zip')
print('Arquivos ZIP criados com sucesso!')

# URL do PDF (Anexo I)
pdf_url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"

# Função para extrair dados das tabelas e concatenar.


def extract_table_from_pdf(pdf_url):
    tables = tabula.read_pdf(pdf_url, pages='all', multiple_tables=True)
    df = pd.concat(tables, ignore_index=True)

    return df


print("Tabelas Extraidas Com Sucesso!!!")

# substituir abreviações.


def replace_abbreviations(df):
    abbreviation_map = {
        "OD": "Outros Dados",
        "AMB": "Ambulatório"
    }
    for col in df.columns:
        df[col] = df[col].replace(abbreviation_map)

    return df


print("Abreviações Substituidas!")

# salva em CSV e compacta em Teste_Marcelo.zip


def save_zip(df, filename):
    csv_filename = filename + ".csv"
    df.to_csv(csv_filename, index=False)
    zip_filename = filename + ".zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(csv_filename)
    os.remove(csv_filename)
    print(f"Arquivo compactado criado: {zip_filename}")


# Extrai as tabelas do pdf, substitui abreviações e salva os dados em um zip.
df = extract_table_from_pdf(pdf_url)

df = replace_abbreviations(df)

save_zip(df, "Teste_Marcelo")

print("Sucesso!!!")
