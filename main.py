import requests
import matplotlib.pyplot as plt
import numpy as np
import pwinput  # type: ignore

url = "http://localhost:3003/medicamentos"
url_farmacia = "http://localhost:3003/farmacia"
url_login = "http://localhost:3003/login"

usuario_id = ""
token = ""


def login():
    titulo("Login do Usuário")

    email = input("E-mail...: ")
    senha = pwinput.pwinput(prompt='Senha....: ')

    response = requests.post(url_login, json={
        "email": email,
        "senha": senha
    })

    if response.status_code == 200:
        resposta = response.json()
        global usuario_id
        global token
        usuario_id = resposta['id']
        token = resposta['token']
        print(f"Ok! Bem-vindo {resposta['nome']}")
    else:
        print("Erro... Não foi possível realizar login no sistema")


def inclusao():
    titulo("Inclusão de medicamentos", "=")

    if token == "":
        print("Erro... Você precisa fazer login para incluir medicamentos")
        return

    nomeMedicamento = input("Nome do Medicamento...: ")
    estoque = int(input("estoque.........: "))
    preco = float(input("Preço R$....: "))
    codigo_barras = int(input("Código de Barras: "))

    response = requests.post(url,
                             headers={"Authorization": f"Bearer {token}"},
                             json={
                                 "nomeMedicamento": nomeMedicamento,
                                 "estoque": estoque,
                                 "codigo_barras": codigo_barras,
                                 "preco": preco,
                                 "farmaciaId": 1,
                                 "usuarioId": usuario_id
                             })

    if response.status_code == 201:
        medicamento = response.json()
        print(f"Ok! medicamento cadastrado com código: {medicamento['codigo_barras']}")
    else:
        print("Erro... Não foi possível incluir o medicamento")


def listagem():
    titulo("Listagem dos medicamentos Cadastrados")

    response = requests.get(url,
                             headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()

    print("Cód. Nome.............: Estoque: Preço R$:")
    print("-------------------------------------------")

    for medicamento in medicamentos:
        print(
            f"{int(medicamento['id']):4d} {medicamento['nomeMedicamento']:20s} {int(medicamento['estoque']):5d} {float(medicamento['preco']):9.2f}")


def alteracao():
    listagem()

    if token == "":
        print("Erro... Você precisa fazer login para alterar medicamentos")
        return

    id = int(input("\nQual o código do medicamento a alterar? "))

    response = requests.get(url)
    medicamentos = response.json()

    medicamento = [x for x in medicamentos if x['id'] == id]

    if len(medicamento) == 0:
        print("Erro... Informe um código existente")
        return

    print(f"Nome do medicamento.: {medicamento[0]['nomeMedicamento']}")
    print(f"codigo_barras........: {medicamento[0]['codigo_barras']}")
    print(f"estoque..............: {medicamento[0]['estoque']}")
    print(f"Preço R$.............: {float(medicamento[0]['preco']):9.2f}")

    novoPreco = float(input("Novo Preço R$: "))

    response = requests.patch(url+"/"+str(id),
                              headers={"Authorization": f"Bearer {token}"},
                              json={"preco": novoPreco})

    if response.status_code == 201:
        medicamento = response.json()
        print("Ok! medicamento alterado com sucesso!")
    else:
        print("Erro... Não foi possível alterar o preço do medicamento")


def exclusao():
    if token == "":
        print("Erro... Você precisa fazer login para excluir medicamentos")
        return

    listagem()

    id = int(input("\nQual código do medicamento você deseja excluir (0: sair)? "))

    if id == 0:
        return

    response = requests.get(url)
    medicamentos = response.json()

    medicamento = [x for x in medicamentos if x['id'] == id]

    if len(medicamento) == 0:
        print("Erro... Informe um código existente")
        return

    print(f"Nome do medicamento.: {medicamento[0]['nomeMedicamento']}")
    print(f"codigo_barras........: {medicamento[0]['codigo_barras']}")
    print(f"estoque..............: {medicamento[0]['estoque']}")
    print(f"Preço R$.............: {float(medicamento[0]['preco']):9.2f}")

    confirma = input("Confirma a exclusão (S/N)? ").upper()

    if confirma == "S":
        response = requests.delete(url+"/"+str(id), 
                                   headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            medicamento = response.json()
            print("Ok! medicamento excluído com sucesso!")
        else:
            print("Erro... Não foi possível excluir este medicamento")


def grafico_por_estabelecimento():
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()
    labels = list(set([x['farmacia']['razaoSocial'] for x in medicamentos]))
    sizes = [0] * len(labels)

    for medicamento in medicamentos:
        index = labels.index(medicamento['farmacia']['razaoSocial'])
        sizes[index] += 1

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title('Nº de medicamentos por empresa')
    plt.gcf().canvas.manager.set_window_title("Gráfico por Empresa")
    ax.pie(sizes, labels=labels)
    plt.show()


def grafico_por_estoque():
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()
    nomes = [x['nomeMedicamento'] for x in medicamentos]
    estoques = [x['estoque'] for x in medicamentos]

    medicamentos_ordenados = sorted(zip(nomes, estoques), key=lambda x: x[1], reverse=True)
    nomes_ordenados, estoques_ordenados = zip(*medicamentos_ordenados)

    fig, ax = plt.subplots(figsize=(9, 5))

    colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'yellow']
    ax.bar(nomes_ordenados, estoques_ordenados, color=colors)
    ax.set_ylabel('Estoques')
    ax.set_title('Medicamentos por estoques')
    plt.show()

def titulo(texto, traco="-"):
    print()
    print(texto)
    print(traco*40)

# ---------------------------- Programa Principal
while True:
    titulo("Cadastro de Veículos")
    print("1. Login do Usuário")
    print("2. Inclusão de medicamentos")
    print("3. Listagem de medicamentos")
    print("4. Alteração de Preço")
    print("5. Exclusão de medicamento")
    print("6. Gráfico de Medicamentos por Farmacias (Pizza)")
    print("7. Gráfico de Medicamentos por Estoque (Colunas)")
    print("8. Finalizar")
    opcao = int(input("Opção: "))
    if opcao == 1:
        login()
    elif opcao == 2:
        inclusao()
    elif opcao == 3:
        listagem()
    elif opcao == 4:
        alteracao()
    elif opcao == 5:
        exclusao()
    elif opcao == 6:
        grafico_por_estabelecimento()
    elif opcao == 7:
        grafico_por_estoque()
    else:
        break
