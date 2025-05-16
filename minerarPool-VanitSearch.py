import requests
import os
import subprocess
import time
import re
import json
import logging
from argparse import ArgumentParser

# Configuração do logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Definir variáveis de configuração via argumentos de linha de comando
parser = ArgumentParser(description="Script para processar blocos de dados relacionados ao Bitcoin.")
parser.add_argument("--pool-token", default=os.getenv("8ce1e93decc9309baf2e52edfb97ac618a31629436d4b2a0d3bf25969384b28c"), required=False, help="Token de autenticação da pool.")
parser.add_argument("--base-url", default="https://bitcoinpuzzles.io/api/block", help="URL base da API.")
parser.add_argument("--interval", type=int, default=0, help="Intervalo de espera entre requisições (em segundos).")
args = parser.parse_args()

POOL_TOKEN = args.pool_token
BASE_URL = args.base_url
INTERVAL = args.interval

headers = {
    "pool-token": POOL_TOKEN,
    "Content-Type": "application/json"
}

def get_block():
    """Obtém um novo bloco ou verifica o status do bloco atual."""
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Lança exceção para códigos de status HTTP 4xx/5xx
        data = response.json()

        # Valida a estrutura do JSON
        if not all(key in data for key in ["status", "id", "range", "position", "checkwork_addresses", "message"]):
            logging.error("Estrutura do JSON inválida.")
            return None

        if data["status"] == 0:
            logging.info(f"Novo bloco recebido: ID {data['id']}")
            logging.info(f"Posição: {data['position']}")
            logging.info(f"Intervalo: {data['range']['start']}:{data['range']['end']}")
            logging.info(f"Endereços de Trabalho: {data['checkwork_addresses']}")
            return data
        else:
            logging.info("Bloco já verificado.")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao conectar à API: {e}")
        return None

def escrever_enderecos_em_arquivo(enderecos):
    """Escreve os endereços de trabalho no arquivo btcadress.txt."""
    with open("btcadress.txt", "w") as f:
        f.write("1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU\n")  # Endereço fixo
        for address in enderecos:
            f.write(f"{address}\n")
    logging.info("Endereços de trabalho escritos em btcadress.txt.")

def executar_script(data):
    """Executa o comando com base no intervalo recebido."""
    start = data["range"]["start"].lstrip("0x")
    end = data["range"]["end"].lstrip("0x")
    enderecos = data["checkwork_addresses"]

    # Escreve os endereços no arquivo btcadress.txt
    escrever_enderecos_em_arquivo(enderecos)

    # Comando para executar o VanitSearch
    comando = [
        './vanitysearch',
        '-t', '0',
        '-gpu',
        '-gpuId', '0',
        '-g', '1792',
        '-o', 'Found.txt',
        '--keyspace', f"{start}:{end}",  # Passa o intervalo sem '0x'
        '-i', 'btcadress.txt'
    ]

    logging.info(f"Executando comando: {' '.join(comando)}")
    try:
        subprocess.run(comando, check=True)

        # Salva o intervalo processado
        with open("SaveRanges.txt", "a") as save_ranges_file:
            save_ranges_file.write(f"{start}:{end}\n")

        # Verifica se a chave foi encontrada
        with open("Found.txt", "r") as found_file:
            if "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU" in found_file.read():
                logging.info("CHAVE 71 ENCONTRADA")
                exit()

        # Extrai as chaves privadas
        hex_pattern = re.compile(r"Priv \(HEX\): 0x\s+([A-Fa-f0-9]+)")
        prefix = "0x0000000000000000000000000000000000000000000000"
        private_keys = []

        with open("Found.txt", "r") as file:
            private_keys = [f"{prefix}{match.group(1)}" for line in file if (match := hex_pattern.search(line))]

        # Envia as chaves privadas para a API
        if private_keys:
            output = {"privateKeys": private_keys}
            response = requests.post(BASE_URL, headers=headers, json=output)
            if response.status_code == 200:
                logging.info(f"Sucesso: {response.json().get('message')}")
                open("Found.txt", "w").close()  # Limpa o arquivo Found.txt
            else:
                logging.error(f"Falha ao enviar as chaves privadas. Status: {response.status_code}, {response.text}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar o comando: {e}")

def main():
    """Inicia o loop principal para obter blocos e executar o script."""
    try:
        while True:
            bloco = get_block()
            if bloco:
                executar_script(bloco)
            else:
                logging.info("Aguardando novo bloco...")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        open("Found.txt", "w").close()
        logging.info("\nExecução interrompida pelo usuário.")

if __name__ == "__main__":
    main()
