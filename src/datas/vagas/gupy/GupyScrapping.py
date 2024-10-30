from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import os
import random
import sys
import requests

class GupyScrapping:
    def __init__(self, url_gupy: str) -> None:
        self.url = url_gupy
        self.urls_vagas: list[str] = []

        options = Options()
        options.add_argument('--headless=new') 
        self.driver = webdriver.Chrome(options=options)
        self.links_falha: list[str] = []

    def salvar_arquivo_texto_em_pasta(self, caminho_pasta: str, nome_arquivo: str, conteudo: list[str]):
        os.makedirs(caminho_pasta, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            for linha in conteudo:
                arquivo.write(linha + '\n')  # Escreve cada string em uma nova linha
            
        print(f"Arquivo salvo em: {nome_arquivo}")

    def salvar_links_com_falha(self):
        diretorio_codigo = os.path.dirname(os.path.abspath(__file__))
        caminho_links_com_falha = os.path.join(f'{diretorio_codigo}', "links_com_falha")
        self.salvar_arquivo_texto_em_pasta(caminho_links_com_falha, "links_falha.txt", self.links_falha)

    def salvar_descricao_vagas(self):
        diretorio_codigo = os.path.dirname(os.path.abspath(__file__))
        caminho_links = os.path.join(f'{diretorio_codigo}', "links")
        caminho_descricoes_vagas = os.path.join(f'{diretorio_codigo}', "descricoes_vagas")
        for index, nome_arquivo in enumerate(os.listdir(caminho_links)):
            print("Processando arquivo:", nome_arquivo)
            caminho_arquivo = os.path.join(caminho_links, nome_arquivo)
            nome_pasta = nome_arquivo.split("-")[0]
            caminho_pasta = os.path.join(caminho_descricoes_vagas, nome_pasta)
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                links_vagas = arquivo.readlines()
            for index, link_vaga in enumerate(links_vagas):
                self.buscar_descricao_vaga(link_vaga, caminho_pasta, f'{index}-{nome_pasta}.txt')
        self.salvar_links_com_falha()

    def buscar_descricao_vaga(self, link_vaga: str, caminho_pasta: str, nome_arquivo: str) -> None:
        try:
            response = requests.get(link_vaga)
            soup = BeautifulSoup(response.text, 'html.parser')
            linhas = []
            linhas.append(f'link_vaga-{link_vaga}')
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'span', 'li']):
                if tag.name in ['h1', 'h2', 'h3']:
                    linhas.append(tag.get_text(strip=True).upper())
                    continue
                linhas.append(tag.get_text(strip=False))

            self.salvar_arquivo_texto_em_pasta(caminho_pasta, nome_arquivo, linhas)
        except:
            self.links_falha.append(link_vaga)
            print("Erro na vaga: ", link_vaga)
    
    def salvar_links_vagas(self, raiz: str, pasta: str, nome_arquivo: str, links: set[str]) -> None:
       # Obtém o diretório onde o script está localizado
        diretorio_codigo = os.path.dirname(os.path.abspath(__file__))
        
        # Define o caminho completo da pasta e do arquivo dentro do diretório do código
        caminho_pasta = os.path.join(f'{diretorio_codigo}', raiz, pasta)
        caminho_arquivo = os.path.join(caminho_pasta, f'{nome_arquivo}-{random.randint(0, sys.maxsize)}.txt')
        
        # Cria a pasta, se não existir
        os.makedirs(caminho_pasta, exist_ok=True)
        
        # Cria e escreve no arquivo
        with open(caminho_arquivo, 'w') as arquivo:
            for linha in links:
                arquivo.write(linha + "\n")
        
        print(f"{len(links)} links salvos em: {caminho_arquivo}")

    
    def buscar_links_vagas_chat(self) -> list[str]:
        # Abra a página desejada
        self.driver.get(self.url)
        time.sleep(5)

        # Localize o elemento `ul` que contém as vagas
        ul_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div/main/ul")

        # Inicializa uma lista para armazenar os links de vagas
        links = []
        prev_length = 0  # Armazena a contagem de `li` para verificar a atualização

        while True:
            # Role a página para o final, usando `Keys.END`
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)  # Aguardar o carregamento das vagas

            # Atualize a lista de `li` para verificar se novas vagas foram carregadas
            li_elements = ul_element.find_elements(By.TAG_NAME, "li")
            
            # Condição de parada: se o número de `li` não aumentou, interrompe o loop
            if len(li_elements) == prev_length:
                break
            prev_length = len(li_elements)

        # Extraia o `href` de cada link `a` dentro de cada `li`
        for li in li_elements:
            try:
                # Encontre a tag <a> dentro de cada <li>
                a_tag = li.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")  # Extrai o link
                # print(f'Link: {href}')
                links.append(href)
            except:
                pass  # Caso algum `li` não tenha um link, ignora

        # Exiba os links extraídos
        # for link in links:
        #     print(link)

        # Feche o driver
        self.driver.quit()

        return links

    def buscar_links_vagas(self) -> list[str]:
        # Abra a página desejada
        self.driver.get(self.url)
        time.sleep(5)

        # Localize o elemento `ul` que contém as vagas
        ul_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div/main/ul")

        # Encontre todos os itens `li` dentro desse `ul`
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # Extraia o `href` de cada link `a` dentro de cada `li`
        links = []
        for li in li_elements:
            try:
                # Encontre a tag <a> dentro de cada <li>
                a_tag = li.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")  # Extrai o link
                self.urls_vagas.append(href)
            except:
                pass  # Caso algum li não tenha um link, ignora

        # Exiba os links extraídos
        for link in links:
            print(link)

        # Feche o self.driver
        self.driver.quit()

        return self.urls_vagas

def main() -> None:
    termos = [
        ("https://portal.gupy.io/job-search/term=backend", "termo_backend_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=frontend", "termo_frontend_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=QA", "termo_QA_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=fullstack", "termo_fullstack_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=full stack", "termo_full_stack_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=back-end", "termo_back_end_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=UX design", "termo_UX_design_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=cientista de dados", "termo_cientista_de_dados_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=UX design", "termo_UX_desing_links_vagas_gupy"),
        ("https://portal.gupy.io/job-search/term=analista de dados", "termo_analista_de_dados_links_vagas_gupy")
        ]
    
    #Código para buscar e salvar os links das buscas no site da GUPY
    # for link, termo in termos:
    #     print(link, termo)
    #     gupy = GupyScrapping(link)
    #     vagas = gupy.buscar_links_vagas_chat()
    #     gupy.salvar_links_vagas(raiz="vagas/gupy", pasta="links", nome_arquivo=termo, links=set(vagas))
    
    #Código para buscar e salvar as descrições das vagas
    # gupy = GupyScrapping("")
    # gupy.salvar_descricao_vagas()
    


if __name__ == "__main__":
    main()