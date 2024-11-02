import os
import random
import sys

class SaverData:

    def __init__(self, diretorio_trabalho: str) -> None:
        caminho_pasta_raiz = os.path.dirname(os.path.abspath(__file__))
        self.diretorio_trabalho = os.path.join(caminho_pasta_raiz, diretorio_trabalho)
        
        print(self.diretorio_trabalho)

    def criar_subpasta(self, caminho_subpasta: str) -> None:
        caminho_pasta = os.path.join(self.diretorio_trabalho, caminho_subpasta)
        os.makedirs(caminho_pasta, exist_ok=True)
    
    def salvar_descricao_vagas(self, subpasta_descricoes: str, nome_arquivo: str, conteudo_descricao: set[str]):
        caminho_descricoes_vagas = os.path.join(self.diretorio_trabalho, subpasta_descricoes)
        
        os.makedirs(caminho_descricoes_vagas, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_descricoes_vagas, nome_arquivo)
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            for linha in conteudo_descricao:
                arquivo.write(linha + "\n")

    def salvar_links(self, subpasta: str, nome_arquivo: str, links: set[str]) -> None:
        caminho_pasta = os.path.join(self.diretorio_trabalho, subpasta)
        caminho_arquivo = os.path.join(caminho_pasta, f'{nome_arquivo}-{random.randint(0, sys.maxsize)}.txt')

        # Cria a pasta, se não existir
        os.makedirs(caminho_pasta, exist_ok=True)
        
        # Cria e escreve no arquivo
        with open(caminho_arquivo, 'w') as arquivo:
            for linha in links:
                arquivo.write(linha + "\n")
        
        print(f"{len(links)} links salvos em: {caminho_arquivo}")

    def recuperar_linhas_arquivo(self, subpasta: str, nome_arquivo: str) -> list[str]:
        caminho_arquivo = os.path.join(self.diretorio_trabalho, subpasta, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
           linhas_arquivo = arquivo.readlines()

        return [linha.strip() for linha in linhas_arquivo]

def main():
    print("SaverData")

if __name__ == "__main__":
    main()