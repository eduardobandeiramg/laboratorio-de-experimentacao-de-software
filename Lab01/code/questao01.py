import requests
from datetime import datetime
import statistics
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Definindo a função para requisição:
def fazerQuery(estrelas):
  token = ""
  url = "https://api.github.com/graphql"
  header = {"Authorization": f"Bearer {token}" , "Content-Type": "application/json"}
  body = f"""query {{
        search(query: "stars:>{estrelas}", type: REPOSITORY, first: 100) {{
            nodes {{
                ... on Repository {{
                    name
                    stargazerCount
                    url
                    createdAt
                }}
            }}
            pageInfo{{
            hasNextPage
            endCursor
            }}
        }}
    }}"""
  resposta = requests.post(url, headers= header, json= {"query": body})
  return resposta

# Definindo a função para requisição COM PAGINAÇÃO:
def fazerQueryComPaginacao(estrelas , aPartirDe):
  token = ""
  url = "https://api.github.com/graphql"
  header = {"Authorization": f"Bearer {token}" , "Content-Type": "application/json"}
  body = f"""query {{
        search(query: "stars:>{estrelas}", type: REPOSITORY, first: 100 , after: "{aPartirDe}") {{
            nodes {{
                ... on Repository {{
                    name
                    stargazerCount
                    createdAt
                }}
            }}
            pageInfo{{
            hasNextPage
            endCursor
            }}
        }}
    }}"""
  resposta = requests.post(url, headers= header, json= {"query": body})
  return resposta

# Recuperando data atual para cálculo da idade dos repositórios:
agora = datetime.now()
# Criando lista para armazenar idades dos repositorios:
idades = []
# Criando variaveis de controle dos loops:
continuaLoop = True
loopDeContagem = True
# Criando variavel para armazenar localizacao do ultimo item:
cursorfinal = ""
# Definindo numero alto de estrelas:
qtdEstrelas = 420000
# Criando lista de linhas para o csv:
linhasDaPlanilha = [["Repositório", "Estrelas", "Criado em", "Idade em anos", "Mediana"]]

while continuaLoop:
  # Reinicializando loop de contagem:
  loopDeContagem = True
  # Criando lista para armazenar repositorios:
  repos = []
  time.sleep(2)
  resposta = fazerQuery(qtdEstrelas)
  if resposta.status_code == 200:
    respostaRequisicao = resposta.json()
    print(f"{len(respostaRequisicao["data"]["search"]["nodes"])} REPOSITÓRIOS NA PRIMEIRA PAGINA")
    while loopDeContagem:
      if len(respostaRequisicao["data"]["search"]["nodes"]) > 0:
        repos.extend(respostaRequisicao["data"]["search"]["nodes"])
      print(f"REPOSITORIOS ENCONTRADOS ATÉ AGORA: {len(repos)}")
      if respostaRequisicao["data"]["search"]["pageInfo"]["hasNextPage"] == False:
        loopDeContagem = False
        print("Nao tem proxima pagina")
      else:
        time.sleep(2)
        cursorfinal = respostaRequisicao["data"]["search"]["pageInfo"]["endCursor"]
        resposta = fazerQueryComPaginacao(qtdEstrelas , cursorfinal)
        respostaRequisicao = resposta.json()
    if len(repos) < 1000:
      qtdEstrelas -= 5000
    else:
      loop = 1
      continuaLoop = False
      for valor in repos:
        print(f"{str(loop)}º Repositório mais popular do GitHub:")
        loop+=1
        print(valor)
        dataCriacao = datetime.strptime(valor["createdAt"] , f"%Y-%m-%dT%H:%M:%SZ")
        idade = agora - dataCriacao
        idades.append(idade.days/365)
        linhasDaPlanilha.append([valor["name"], valor["stargazerCount"], valor["createdAt"], idade , statistics.median(idades)])
      print(f"Lista das idades: {idades}")
      print(f"Mediana das idades: {statistics.median(idades)} anos")
      # Gerando a planilha com os dados obtidos:
      with open("questao01.csv", mode= "w", newline= "", encoding= "utf-8") as arquivo:
        csv.writer(arquivo).writerows(linhasDaPlanilha)
      # Gerando o gráfico com os dados obtidos:
      #plt.hist(idades, bins=16, color='skyblue', edgecolor='black' , )
      sns.histplot(idades, kde=True)
      plt.title('Distribuição das "idades" dos repositórios em anos')
      plt.xlabel('Idades')
      plt.ylabel('Frequência')
      plt.show()
    # Gerando o gráfico boxplot:
      plt.boxplot(idades)
      plt.title('Distribuição das "idades" dos repositórios em anos')
      plt.xlabel("Idades")
      plt.ylabel("Frequência")
      plt.show()

  else:
    print("Erro ao acessar API do GitHub")
    print("Descrição do erro:")
    print(resposta.status_code)