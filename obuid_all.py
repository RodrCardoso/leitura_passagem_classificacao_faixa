import os
import sys

def process_files(input_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    input_files = [os.path.join(input_directory, file) for file in os.listdir(input_directory)]

    for file_path in input_files:
        if os.path.isfile(file_path) and file_path.endswith(".txt"):  # Adicione esta verificação
            process_file(file_path, output_directory)

def process_file(file_path, output_directory):
    data = []
    current_type = None

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('*I'):
                parts = line.strip().split()
                record_type = parts[6]

                if record_type != current_type:
                    if current_type is not None:
                        save_records(current_type, data, output_directory, file_path)

                    current_type = record_type
                    data = []

                data.append(line)

    if current_type is not None:
        save_records(current_type, data, output_directory, file_path)

def save_records(record_type, records, output_directory, file_path):
    #_, file_extension = os.path.splitext(os.path.basename(records[0]))
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    output_filename = f"{file_name}_{record_type}.txt"
    output_path = os.path.join(output_directory, output_filename)
    # print(output_filename)

    with open(output_path, 'a') as output_file:
        output_file.write(''.join(records))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <diretorio>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = os.path.join(input_directory, f'sls_{os.path.basename(input_directory)}')
    process_files(input_directory, output_directory)
