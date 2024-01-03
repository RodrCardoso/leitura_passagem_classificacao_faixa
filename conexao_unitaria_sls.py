import paramiko
import sys
import time
import threading
import os


def ssh_connect(hostname, username, password, max_attempts=3):
    attempt = 1
    while attempt <= max_attempts:
        print(f"Tentativa {attempt} de conectar em {hostname}...")
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=username, password=password)
            print(f"Conexão estabelecida com sucesso em {hostname}.")
            return client
        except Exception as e:
            print(f"Não foi possível estabelecer conexão em {hostname}. Erro: {e}")
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
            print(chunk, end='', flush=True)  # Adiciona um print do que está sendo lido

def get_next_suffix(suffix_file):

    if os.path.exists(suffix_file):
        with open(suffix_file, "r") as file:
            count = int(file.read().strip())
    else:
        count = 0

    with open(suffix_file, "w") as file:
        file.write(str(count + 1))

    return count

def main():
    # Verificar se o número correto de argumentos foi fornecido
    if len(sys.argv) != 3:
        print("Uso: python script.py <modelo> <sufixo>")
        sys.exit(1)

    # Obter o sufixo e senha a partir dos argumentos de linha de comando
    modelo = sys.argv[1]
    sufixo = sys.argv[2]
    caminho_destino = sys.argv[2]
    password = 'IddqdIdkfa'

    # Informações de conexão SSH
    hostname = f'sp-{modelo}-f290-v1-{sufixo}'
    username = 'pi'

    # Comando a ser executado via nc
    nc_command = "nc localhost 23"

    # Conectar via SSH
    client = ssh_connect(hostname, username, password)

    try:
        # Lista para armazenar chunks da saída (thread-safe)
        output_list = []
        # Lock para garantir acesso seguro à variável output_list
        output_lock = threading.Lock()

        # Executar o comando nc
        channel = run_command(client, nc_command)

        # Iniciar a leitura em uma thread separada
        stop_event = threading.Event()
        output_thread = threading.Thread(target=read_output, args=(channel, stop_event, output_lock, output_list))
        output_thread.start()

        # Aguardar entrada do teclado para encerrar a leitura
        input("Pressione Enter para encerrar a leitura...\n")
        stop_event.set()  # Sinalizar a thread para encerrar

        # Aguardar até que a thread termine
        output_thread.join()
        suffix_file = f'sls_{sufixo}_passagem_'
        # Obter o sufixo crescente
        suffix_count = get_next_suffix(suffix_file)

        # Construir o caminho completo do diretório
        output_directory = os.path.join(caminho_destino, str(modelo))

        # Criar o diretório se não existir
        os.makedirs(output_directory, exist_ok=True)

        # output_filename = f'{suffix_file}{suffix_count}.txt'
        output_filename = os.path.join(caminho_destino, f'{suffix_file}{suffix_count}.txt')

        # Concatenar chunks e salvar a saída em um arquivo
        with open(output_filename, 'w') as output_file:
            with output_lock:
                output_file.write(''.join(output_list))

    except Exception as e:
        print(f"Erro: {e}")

    finally:
        # Fechar a conexão SSH
        client.close()

if __name__ == "__main__":
    main()
