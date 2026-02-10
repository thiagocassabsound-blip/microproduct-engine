import os

dirs = [
    "execucao", "diretivas", "radar", "produtos", "paginas", "deploy",
    "telemetria", "pricing", "upgrade", "guardian", "logs", "temp",
    "credenciais", "memory"
]

base_path = "c:/Users/Cliente/Downloads/fastoolhub.com/microproduct-autonomous-system"

for d in dirs:
    path = os.path.join(base_path, d)
    os.makedirs(path, exist_ok=True)
    print(f"Created: {path}")

# Create empty __init__.py in python modules to make them packages
py_modules = ["execucao", "radar", "produtos", "paginas", "deploy", "telemetria", "pricing", "upgrade", "guardian"]
for m in py_modules:
    init_path = os.path.join(base_path, m, "__init__.py")
    with open(init_path, 'w') as f:
        pass
    print(f"Created package init: {init_path}")
