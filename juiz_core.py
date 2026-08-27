import subprocess
import tempfile
import sys
import ast
import json
from pathlib import Path

def verificar_codigo_seguro(codigo):
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

    para_bloquear = {"os", "sys", "subprocess", "shutil", "pathlib", "socket"}
    
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.split('.')[0] in para_bloquear:
                    return False, f"SecurityError: Uso de biblioteca proibida '{alias.name}'"
        elif isinstance(no, ast.ImportFrom):
            if no.module and no.module.split('.')[0] in para_bloquear:
                return False, f"SecurityError: Uso de biblioteca proibida '{no.module}'"
        elif isinstance(no, ast.Call):
            if isinstance(no.func, ast.Name) and no.func.id in {"open", "eval", "exec", "compile"}:
                return False, f"SecurityError: Função restrita '{no.func.id}()'"
                
    return True, ""

# Código embutido para criar a estrutura do LeetCode nos bastidores
DRIVER_TEMPLATE = """
import sys
import json

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def list_to_link(lst):
    if not lst: return None
    h = ListNode(lst[0])
    c = h
    for v in lst[1:]:
        c.next = ListNode(v)
        c = c.next
    return h

def link_to_list(node):
    r = []
    while node:
        r.append(node.val)
        node = node.next
    return r

# --- CODIGO DO ALUNO ---
{codigo_aluno}
# -----------------------

if __name__ == '__main__':
    try:
        raw_input = sys.stdin.read()
        if not raw_input: sys.exit(0)
        args = json.loads(raw_input)
        
        # Converte as entradas (como 'head') para Linked Lists
        kwargs = {{}}
        for k, v in args.items():
            if k.startswith('head'): 
                kwargs[k] = list_to_link(v)
            else: 
                kwargs[k] = v
                
        # Chama a função do aluno
        result = {funcao_alvo}(**kwargs)
        
        # Converte o retorno para lista (se for um Nó) para facilitar a comparação
        if isinstance(result, ListNode): 
            out = link_to_list(result)
        elif result is None: 
            out = [] # Se a função deveria retornar head e retornou None, consideramos lista vazia
        else: 
            out = result
            
        print(json.dumps({{"sucesso": True, "saida": out}}))
    except Exception as e:
        import traceback
        erro_limpo = traceback.format_exc().split("File \\\"<string>\\\"")[-1]
        print(json.dumps({{"sucesso": False, "erro": str(e), "traceback": erro_limpo}}))
"""

def corrigir_codigo(codigo, testes, funcao_alvo, timeout=1):
    resultados = []
    acertos = 0
    total = len(testes)

    seguro, msg_erro = verificar_codigo_seguro(codigo)
    if not seguro:
        for i, caso in enumerate(testes, start=1):
            resultados.append({
                "teste": i, "passou": False, "status": "Compilation Error",
                "saida_obtida": "", "saida_esperada": str(caso.get("saida", "")), "erro": msg_erro
            })
        return {"acertos": 0, "total": total, "resultados": resultados}

    codigo_pronto = DRIVER_TEMPLATE.format(codigo_aluno=codigo, funcao_alvo=funcao_alvo)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp:
        temp.write(codigo_pronto)
        arquivo_temp = temp.name

    try:
        for i, caso in enumerate(testes, start=1):
            entrada_dict = caso.get("entrada", {})
            saida_esperada = caso.get("saida", "")

            try:
                # Passa a entrada do teste via STDIN em formato JSON
                execucao = subprocess.run(
                    [sys.executable, arquivo_temp],
                    input=json.dumps(entrada_dict), text=True, capture_output=True, timeout=timeout
                )

                if execucao.returncode != 0:
                    resultados.append({
                        "teste": i, "passou": False, "status": "Runtime Error",
                        "saida_obtida": "", "saida_esperada": str(saida_esperada), 
                        "erro": execucao.stderr.strip()
                    })
                    continue

                # Pega a resposta do código injetado
                resposta_driver = json.loads(execucao.stdout)
                
                if not resposta_driver.get("sucesso"):
                    resultados.append({
                        "teste": i, "passou": False, "status": "Runtime Error",
                        "saida_obtida": "", "saida_esperada": str(saida_esperada), 
                        "erro": resposta_driver.get("traceback", resposta_driver.get("erro"))
                    })
                else:
                    saida_obtida = resposta_driver.get("saida")
                    if saida_obtida == saida_esperada:
                        acertos += 1
                        status = "Accepted"
                        passou = True
                    else:
                        status = "Wrong Answer"
                        passou = False
                        
                    resultados.append({
                        "teste": i, "passou": passou, "status": status,
                        "saida_obtida": str(saida_obtida), "saida_esperada": str(saida_esperada), "erro": ""
                    })

            except subprocess.TimeoutExpired:
                resultados.append({
                    "teste": i, "passou": False, "status": "Time Limit Exceeded",
                    "saida_obtida": "", "saida_esperada": str(saida_esperada), 
                    "erro": f"Tempo esgotado ({timeout}s). Verifique loops infinitos nos ponteiros."
                })

    finally:
        Path(arquivo_temp).unlink(missing_ok=True)

    return {"acertos": acertos, "total": total, "resultados": resultados}