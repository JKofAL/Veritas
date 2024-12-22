import subprocess

def compile_and_run(file_path, executable_path, input_path):
    try:
        compile_command = f"g++ {file_path} -o {executable_path}"
        subprocess.run(compile_command, shell=True, check=True, stderr=subprocess.PIPE)

        with open(input_path, "r") as input_file:
            result = subprocess.run(executable_path, stdin=input_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            return result.stdout.decode('utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        return f"Compilation error: {e.stderr.decode('utf-8', errors='replace')}"