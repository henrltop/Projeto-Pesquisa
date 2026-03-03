import requests
import os
import json

def buscar_e_baixar_iomat(palavra_chave):
    # AQUI ESTAVA O SEGREDO! O endpoint correto é o v1/buscas
    url_busca = "https://api.iomat.mt.gov.br/busca/v1/buscas"
    
    headers = {
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # O parâmetro correto revelado pelo Curl é 'q'
    params = {
        'q': palavra_chave
    }
    
    print(f"\n[+] Buscando pela palavra: '{palavra_chave}'...")
    
    try:
        response = requests.get(url_busca, params=params, headers=headers)
        
        # Verifica se deu algum erro
        if response.status_code != 200:
            print(f"[-] O servidor retornou o erro {response.status_code}.")
            print(f"[-] Resposta do servidor: {response.text}")
            return
            
        resultados = response.json()
        
        # Navegando na estrutura do JSON (lida tanto com a raiz quanto dentro de 'data')
        if 'data' in resultados and len(resultados['data']) > 0:
            es_data = resultados['data'][0]
        else:
            es_data = resultados
            
        if 'hits' not in es_data or 'hits' not in es_data['hits']:
            print("[-] Nenhum resultado encontrado com essa palavra.")
            return
            
        lista_documentos = es_data['hits']['hits']
        
        # O Elasticsearch pode retornar o total como um número ou um dicionário
        total_obj = es_data['hits']['total']
        total_encontrado = total_obj if isinstance(total_obj, int) else total_obj.get('value', 0)
        
        print(f"[+] Sucesso! O servidor encontrou {total_encontrado} menções.\n")
        
        # Cria a pasta
        pasta_destino = f"resultados_{palavra_chave.replace(' ', '_')}"
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Salva os resultados
        for item in lista_documentos:
            source = item.get('_source', {})
            
            diario_id = source.get('diario_id')
            pagina = source.get('pagina')
            ano = source.get('year', 'AnoDesconhecido')
            data_pub = source.get('data', 'DataDesconhecida')
            
            # Pega o texto (às vezes vem como lista, às vezes como string simples)
            texto_bruto = source.get('conteudo', '')
            texto_conteudo = texto_bruto[0] if isinstance(texto_bruto, list) else texto_bruto
            
            edicao = item.get('suplemento', f"Diario_{diario_id}")
            
            # Monta o link clicável
            url_iomat = f"https://www.iomat.mt.gov.br/portal/visualizacoes/pdf/{diario_id}#/p:{pagina}/e:{diario_id}"
            
            print(f" -> Encontrado: Ano {ano} | Data: {data_pub} | Edição: {edicao} | Página: {pagina}")
            
            # Monta o arquivo TXT
            nome_arquivo_txt = f"{ano}_{data_pub}_edicao_{diario_id}_pag_{pagina}.txt"
            caminho_salvar = os.path.join(pasta_destino, nome_arquivo_txt)
            
            with open(caminho_salvar, 'w', encoding='utf-8') as f:
                f.write(f"Link Original do PDF: {url_iomat}\n")
                f.write(f"Data de Publicação: {data_pub}\n")
                f.write(f"{edicao} | Página: {pagina}\n")
                f.write("=" * 60 + "\n\n")
                f.write(texto_conteudo)
                
            print(f"    [OK] Salvo em: {nome_arquivo_txt}\n")
            
        print(f"[!] Processo finalizado. Verifique a pasta '{pasta_destino}'.")

    except Exception as e:
        print(f"[-] Ocorreu um erro no script: {e}")

if __name__ == "__main__":
    palavra = input("Digite a palavra para buscar no IOMAT: ")
    buscar_e_baixar_iomat(palavra)