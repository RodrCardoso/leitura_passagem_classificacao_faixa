import os

def process_file(file_path):
    data = []
    current_type = None

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('*I'):
                parts = line.strip().split()
                record_type = parts[6]

                if record_type != current_type:
                    if current_type is not None:
                        save_records(current_type, data)

                    current_type = record_type
                    data = []

                data.append(line)

    if current_type is not None:
        save_records(current_type, data)

def save_records(record_type, records):
    output_directory = 'output'  # Altere para o diretório desejado
    output_filename = f"{record_type}.txt"
    output_path = os.path.join(output_directory, output_filename)

    with open(output_path, 'a') as output_file:
        output_file.write(''.join(records))

if __name__ == "__main__":
    input_file = '0046/sls_0046_passagem_1.txt'  # Altere para o nome do seu arquivo
    process_file(input_file)