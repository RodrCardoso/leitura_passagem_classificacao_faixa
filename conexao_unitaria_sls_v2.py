import paramiko
import sys
import threading
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

def ssh_connect(hostname, username, password, max_attempts=3):
    attempt = 1
    while attempt <= max_attempts:
        logging.info(f"Tentativa {attempt} de conectar em {hostname}...")
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=username, password=password)
            logging.info(f"Conexão estabelecida com sucesso em {hostname}.")
            return client
        except Exception as e:
            logging.error(f"Não foi possível estabelecer conexão em {hostname}. Erro: {e}")
            attempt += 1

    raise Exception(f"Excedeu o número máximo de tentativas de conexão em {hostname}.")

def run_command(client, command):
    channel = client.invoke_shell()
    channel.send(command + "\n")
    while not channel.recv_ready():
        pass
    channel.recv(4096)  # Limpar qualquer saída inicial
    return channel

def read_output(channel, stop_event, output_lock, output_list):
    while not stop_event.is_set():
        if channel.recv_ready():
            chunk = channel.recv(1).decode('utf-8')
            with output_lock:
                output_list.append(chunk)
            logging.info(chunk, end='', flush=True)  # Adiciona um log do que está sendo lido

def get_next_suffix(suffix_file):
    if os.path.exists(suffix_file):
        with open(suffix_file, "r") as file:
            count = int(file.read().strip())
    else:
        count = 1

    with open(suffix_file, "w") as file:
        file.write(str(count + 1))

    return count

def main():
    if len(sys.argv) != 3:
        logging.error("Uso: python script.py <modelo> <sufixo>")
        sys.exit(1)

    modelo = sys.argv[1]
    sufixo = sys.argv[2]
    caminho_destino = sys.argv[2]
    password = 'IddqdIdkfa'

    hostname = f'sp-{modelo}-f290-v1-{sufixo}'
    username = 'pi'
    nc_command = "nc localhost 23"

    while True:
        client = ssh_connect(hostname, username, password)

        try:
            output_list = []
            output_lock = threading.Lock()

            channel = run_command(client, nc_command)

            stop_event = threading.Event()
            output_thread = threading.Thread(target=read_output, args=(channel, stop_event, output_lock, output_list))
            output_thread.start()

            logging.info("Aguardando 1,5 minutos antes de encerrar a leitura...")
            time.sleep(90)  # Aguardar 1,5 minutos (90 segundos)

            stop_event.set()
            output_thread.join()

            output_directory = os.path.join(caminho_destino)
            os.makedirs(output_directory, exist_ok=True)

            suffix_file = os.path.join(caminho_destino, f'sls_{sufixo}_passagem_')
            suffix_count = get_next_suffix(suffix_file)

            output_filename = f'{suffix_file}{suffix_count}.txt'

            with open(output_filename, 'w') as output_file:
                with output_lock:
                    output_file.write(''.join(output_list))

            logging.info(f"Leitura concluída. Aguardando próximo ciclo...")

        except Exception as e:
            logging.error(f"Erro: {e}")

        finally:
            client.close()

if __name__ == "__main__":
    main()
