import subprocess
import threading

def executar_script(modelo, sufixo):
    comando = f"python3 conexao_unitaria_sls.py {modelo} {sufixo}"
    try:
        subprocess.run(comando, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando para {modelo}-{sufixo}: {e}")

equipamentos = [
    ("gw", "0207"),
    ("gw", "0536"),
    ("gw", "0397"),
    ("gw", "0077"),
    ("gw", "0046"),
    # Adicione outros equipamentos conforme necessário
]

threads = []

for modelo, sufixo in equipamentos:
    thread = threading.Thread(target=executar_script, args=(modelo, sufixo))
    thread.start()
    threads.append(thread)

# Aguardar a conclusão de todas as threads
for thread in threads:
    thread.join()

print("Todos os scripts foram executados.")
