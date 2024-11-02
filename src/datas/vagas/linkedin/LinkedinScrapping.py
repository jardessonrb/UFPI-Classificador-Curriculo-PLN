from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
from bs4 import BeautifulSoup
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from datas.SaverData import SaverData


class LinkedinScraper:

    def __init__(self, pasta_raiz: str, termo_pesquisa: str, link_base: str) -> None:
        self.link_login = "https://www.linkedin.com/login/pt?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
        self.link_base_vagas = link_base
        self.saver_data = SaverData(diretorio_trabalho = pasta_raiz)
        self.termo_pesquisa = termo_pesquisa

        options = Options()
        # options.add_argument('--headless=new') 
        self.driver = webdriver.Chrome(options=options)

    def login(self, password: str, email: str) -> None:
    
        # Abre a página de login
        self.driver.get(self.link_login)
        print("Esperando pagina de login carregar")
        time.sleep(12)  # Espera o carregamento da página
        
        # Insere o email
        email_input = self.driver.find_element(By.ID, "username")
        email_input.send_keys(email)

        # Insere a senha
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        # Clica no botão de login
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Entrar']"))
        )
        login_button.click()

        # Espera um tempo para o LinkedIn carregar a página inicial após o login
        time.sleep(10)
        
        # Checa se o login foi bem-sucedido verificando a URL atual
        if "feed" in self.driver.current_url:
            print("Login bem-sucedido.")
        else:
            print("Falha no login. Verifique suas credenciais.")

    def buscar_links_vagas(self) -> None:

        pagina = 0
        links_salvos = []
        while True:
            paginacao = pagina * 25
            url_vagas = ""
            if paginacao > 0:
                url_vagas = self.link_base_vagas + f'&start={paginacao}'
            else:
                url_vagas = self.link_base_vagas
            
            pagina += 1

            try:
                self.driver.get(url_vagas)
                print("Esperando pagina de vagas carregar")
                time.sleep(5)  # Aguarda carregar a página

                # links_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.disabled.ember-view.job-card-container__link.job-card-list__title.job-card-list__title--link")
                
                # links_vagas = [link.get_attribute("href") for link in links_elements]
                # links_salvos.extend(links_vagas)
                # print(f'Links da página {pagina + 1} - qnt: {len(links_vagas)}')

                # Localiza o elemento `ul` que contém as vagas
                ul_element = self.driver.find_element(By.CLASS_NAME, "scaffold-layout__list-container")
                
                # Realiza a rolagem para garantir que todos os `li` sejam carregados
                self.driver.execute_script("arguments[0].scrollIntoView(false);", ul_element)
                time.sleep(2)  # Aguarda o carregamento dos novos itens
                self.driver.execute_script("arguments[0].scrollIntoView(false);", ul_element)
                time.sleep(2)  # Aguarda o carregamento dos novos itens
                self.driver.execute_script("arguments[0].scrollIntoView(false);", ul_element)
                time.sleep(2)  # Aguarda o carregamento dos novos itens

                # Extraindo links dos elementos `<a>` nos `<li>` carregados
                links_elements = ul_element.find_elements(By.CSS_SELECTOR, "a.disabled.ember-view.job-card-container__link.job-card-list__title.job-card-list__title--link")
                links_vagas = [link.get_attribute("href") for link in links_elements]
                links_salvos.extend(links_vagas)
                print(f'Pagina {pagina} - Quantidade de elementos de vagas: {len(links_vagas)}')

            except:
                pagina = -1

            if pagina < 0:
                break
            if len(links_salvos) > 500:
                break
            if len(links_vagas) == 0:
                    break
            
        self.salvar_links(links_salvos)
        
    def salvar_links(self, links: list[str]) -> None:
        self.saver_data.salvar_links("links", f'{self.termo_pesquisa}-{random.randint(0, sys.maxsize)}', set(links))
        print("Links salvos")

    def salvar_descricao(self, link: str) -> None :
        self.driver.get(link)
        print("Esperando descricao")
        time.sleep(5)  # Aguarda a página carregar completamente
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extraindo o título da vaga
        try:
            titulo = soup.select_one('h1.t-24.t-bold.inline').get_text(strip=True)
        except Exception as e:
            print(f"Erro ao encontrar o título na vaga: {link}. Erro: {str(e)}")
            

        # Extraindo todo o texto do artigo usando BeautifulSoup
        try:
            artigo = soup.select_one('article.jobs-description__container')
            # descricao = artigo.get_text(strip=True)
            descricoes = []
            descricoes.append(f'link-{link}')
            descricoes.append(titulo)
            for tag in artigo.find_all(['h1', 'h2', 'h3', 'span', 'p', 'li']):
                descricoes.append(tag.get_text(strip=True))

        except Exception as e:
            print(f"Erro ao encontrar a descrição na vaga: {link}. Erro: {str(e)}")
            

        self.saver_data.salvar_descricao_vagas(subpasta_descricoes="descricoes_vagas", nome_arquivo=f'{self.termo_pesquisa}-{random.randint(0, sys.maxsize)}.txt', conteudo_descricao=set(descricoes))
        # self.driver.quit()

def main():

    path_atual = os.path.dirname(os.path.abspath(__file__))
    path_credenciais = os.path.join(path_atual, "..", "..", "..", "credenciais\linkedin.txt")
    with open(path_credenciais, 'r') as arquivo:
        linhas = [linha.strip() for linha in arquivo.readlines()]

    password = linhas[0]
    usename  = linhas[1]


    link_base_vagas = "https://www.linkedin.com/jobs/search/?currentJobId=4006319340&f_TPR=r2592000&geoId=106057199&keywords=(%22backend%22%20OR%20%22Backend%22%20OR%20%22back-end%22%20OR%20%22BackEnd%22%20OR%20%22Back-End%22%20OR%20%22back%20end%22)%20NOT%20(%22estagio%22%20OR%20%22Estagio%22%20OR%20%22Software%20Engineer%22%20OR%20%22Estagi%C3%A1rio%22)&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
    linkedin = LinkedinScraper(pasta_raiz="vagas/linkedin", termo_pesquisa=f'backend_back_end_BackEnd_Back_End', link_base = link_base_vagas)
    linkedin.login(password, usename)
    linkedin.buscar_links_vagas()

    # path_salvar_links = os.path.join(path_atual, "..", "..", "..", "credenciais\links.txt")
    # os.makedirs(path_salvar_links, exist_ok=True)

    # links_buscados = linkedin.buscar_links_vagas()

    # linkedin.salvar_links(links=links_buscados)
    # for link in links_buscados:
    #     print(link)
    
    # link_vagas = ["https://www.linkedin.com/jobs/view/4063213870/?eBP=CwEAAAGS6qYvzXFijgiRWEGp6AUdcd-98cVLqdaln3tyckTRMAYL663BXZiidPPA36WTGDweUZJtjxHfVyz1wJK7TQCenx758fSHj3xa2bggCjb6oNZzEwsry4Ga-ytJeqLpGlWGGb7pGDh5qaG-lt7sCisQ6NsmNUA_7bpvH2aHimF8PQG-7cfaiDBA1r_fq85FqyqtxA3C-uGbA2geuoAqNo9VKhBbgHiBXe0TQZ1FZ0kexb7QU0VWKE_pmMcjZtECdM0wJ-ed7a52Ex7hKa0hGUm6wPnevVx_qOIDicdTUztCpwkQE5Rf6VESqELZtHHyXWISSAF-5a6JBRCcF2ey8kdZHLXh-gv-wGUbS_dcQry7NaR0_dTFWpapJpL1nrme-nsD8OZeBlE-yf0xcKGVkxrVYdiVd_NQMKPQ42-wbe9jIScs2PLIw-6n2Dz21t6OHcmZSEsZexR1-2vYKktujacjPv9tPdo-msPWALCuOH2Sg4kzkdsn40sIbT76N1AwdYSQDy8AfZZmsjJX09bp13HKN5de1nM&refId=zm0flW96jfi5FTgIAE76cw%3D%3D&trackingId=tpvsPUYqGUbqRPKREGtiiQ%3D%3D&trk=flagship3_search_srp_jobs",
    #             "https://www.linkedin.com/jobs/view/4062498561/?eBP=CwEAAAGS6qYvzbSmz-R4lE8wNYFcYCGIV6esLom0WQFiHsM_eYb19m0o9dZiiuknKmatJal0Yr1fCi-G1MK67OJ79HeLWqMX62OXaGHbbLLsm3LsIdeL_QYg-8JmXZdiuCHOsXqO7P7PFD2gQXrkl4f7zJh31tlZVgwC8zLJt4XpESqRsdkbvAkdXpb9cNik61ii9vktKG25G7nsVyIiEWB2mfgd1UpMTs-ny8pOP-xoE3-fFkoXXKfjz3K4Sthxl1lXcTTfWJKOb34AuArQFUIJRT6GmgimEfr038tqiB2yXREsoJ0Lm7SVlUQzq5FC6XUmhQWB2Y5Ig6sZjO6iWLvBHNBoLK8wkwueZ1QPM0AA3qTGtJDd7-yTZynJlbaanGhIfKreqh-PAw3a5aBoJt2yWMCKtpmcc4uRcl54JhUQ5G3mqdgrykRiFeZFPuB8ub_hY_dEaDeTxA&refId=zm0flW96jfi5FTgIAE76cw%3D%3D&trackingId=0KneGAP5rbJwkZ1CKhvREw%3D%3D&trk=flagship3_search_srp_jobs"]
    
    # for link in link_vagas:
    #     linkedin.salvar_descricao(link)
if __name__ == "__main__":
    main()