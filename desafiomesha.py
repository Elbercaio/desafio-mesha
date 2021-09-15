from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re
import pandas as pd
import matplotlib.pyplot as plt

# Gerando Pedido
pedido = Request('https://dados.gov.br/dataset/serie-historica-de-precos-de-'
                 'combustiveis-por-revenda')
with urlopen(pedido) as resposta:
    # Lendo dados
    dados = resposta.read()
    texto = dados.decode('utf-8')
    # Separando os links
    links = re.findall('href="(.*csv)"', texto)
    links_g = [link for link in links if 'gasolina' in link
               and 'landpage' not in link]
    dfs = []
    medias = []
    meses = []
    for link in links_g:
        # Tentando ler os links como csvs
        try:
            df = pd.read_csv(link, sep=';')
        except HTTPError as e:
            print(f'Para o link: {link}')
            print('O servidor não conseguiu cumprir o pedido.')
            print('Código de erro: ', e.code)
        except URLError as e:
            print('Falhamos em alcançar o servidor.')
            print('Motivo: ', e.reason)
        else:
            # Tratando coluna de preços
            precos = df["Valor de Venda"].apply(lambda x: x.replace(',', '.'))
            precos = pd.to_numeric(precos, downcast="float")
            df["Valor de Venda"] = precos
            # Calculando a média da gasolina no mês para o plot de barras
            media = df.groupby(['Produto'])['Valor de Venda'].mean()
            medias.append(media.loc['GASOLINA'])
            # Salvando mês para o plot de barras
            data = df['Data da Coleta'].loc[0][3:]
            meses.append(data)
            # Analisando vantagem de compra do etanol no mês 04
            if data == '04/2021':
                # Agrupando por produto e estado
                vantagem = pd.DataFrame({'Media': df.groupby(
                    ['Estado - Sigla', 'Produto'])['Valor de Venda'].mean(
                )}).reset_index()
                vantajosos = []
                # Checando critério de vantagem
                for estado in df['Estado - Sigla'].unique():
                    df_estado = vantagem[vantagem['Estado - Sigla'] == estado]
                    gasolina = df_estado[
                        df_estado['Produto'] == 'GASOLINA'].reset_index().at[
                        0, 'Media']
                    etanol = df_estado[
                        df_estado['Produto'] == 'ETANOL'].reset_index().at[
                        0, 'Media']
                    if etanol / gasolina < 0.7:
                        vantajosos.append(estado)

            dfs.append(df)

# Agrupando dados para análise anual
df_total = pd.concat(dfs, ignore_index=True)
# Achando os maiores valores
maiores_valores = df.groupby(['Estado - Sigla'])['Valor de Venda'].max()

# Plotando gráfico de barras
plt.bar(meses, medias)
plt.title("Média de valor da gasolina pôr mês em 2021")
plt.xlabel("Meses")
plt.ylabel("Preço da Gasolina (R$)")
plt.ylim(4, 7)
plt.show()

# Resultados
print('1. No ano de 2021, qual o maior valor da gasolina por estado?')
print(maiores_valores, '\n')
print('2. Gere um gráfico em barras da média de valor da gasolina pôr mês em '
      '2021\n')
plt.show()
print('3. No mês 04/2021, identifique qual(ais) as cidade(s) que abastecer '
      'com etanol é mais vantajoso do que gasolina?')
print('As cidade são:')
for vantajosa in vantajosos:
    print(vantajosa)
