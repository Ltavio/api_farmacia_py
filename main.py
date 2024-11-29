import requests
import matplotlib.pyplot as plt
import numpy as np
import pwinput  # type: ignore

url = "http://localhost:3000/medicamentos"
url_login = "http://localhost:3000/login"

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

    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()

    print("Cód. Barras.............: Nome .........: Estoque: Preço R$:")
    print("------------------------------------------------------------")

    for medicamento in medicamentos:
        print(
            f"{medicamento['codigo_barras']:4d} {medicamento['nomeMedicamento']:20s} {medicamento['estoque']:15s} {float(medicamento['preco']):9.2f}")


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

    print(f"\Nome do medicamento.: {medicamento[0]['nomeMedicamento']}")
    print(f"codigo_barras........: {medicamento[0]['codigo_barras']}")
    print(f"estoque..............: {medicamento[0]['estoque']}")
    print(f"Preço R$.............: {float(medicamento[0]['preco']):9.2f}")

    novoPreco = float(input("Novo Preço R$: "))

    response = requests.put(url+"/"+str(id),
                              headers={"Authorization": f"Bearer {token}"},
                              json={"preco": novoPreco})

    if response.status_code == 200:
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

    print(f"\Nome do medicamento.: {medicamento[0]['nomeMedicamento']}")
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


def grafico():
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()
    labels = list(set([x['marca'] for x in medicamentos]))
    sizes = [0] * len(labels)

    for medicamento in medicamentos:
        index = labels.index(medicamento['marca'])
        sizes[index] += 1

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title('Nº Veículos por Marca')
    plt.gcf().canvas.manager.set_window_title("Gráfico por Marcas")
    ax.pie(sizes, labels=labels)
    plt.show()


def grafico2():
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()
    marcas = tuple(set([x['marca'] for x in medicamentos]))
    quant_seminovos = [0] * len(marcas)
    quant_usados = [0] * len(marcas)

    for medicamento in medicamentos:
        index = marcas.index(medicamento['marca'])
        if medicamento['ano'] == 2023 or medicamento['ano'] == 2024:
            quant_seminovos[index] += 1
        else:
            quant_usados[index] += 1

    tipos_quants = {
        "Seminovos": quant_seminovos,
        "Usados": quant_usados
    }
    width = 0.5

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(marcas))

    for tipo, quants in tipos_quants.items():
        p = ax.bar(marcas, quants, width, label=tipo, bottom=bottom)
        bottom += quants

    ax.set_title("Nº de Veículos por Marca e Tipo")
    plt.gcf().canvas.manager.set_window_title("Gráfico por Marcas")
    ax.legend(loc="upper left")

    plt.show()

def grafico3():
    response = requests.get(url)

    if response.status_code != 200:
        print("Erro... Não foi possível acessar a API")
        return

    medicamentos = response.json()
    combustiveis = tuple(set([x['combustivel'] for x in medicamentos]))
    quants = [0] * len(combustiveis)

    for medicamento in medicamentos:
        index = combustiveis.index(medicamento['combustivel'])
        quants[index] += 1

    fig, ax = plt.subplots(figsize=(9, 5))

    y_pos = [i for i in range(len(combustiveis))]

    colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'yellow']
    ax.barh(y_pos, quants, align='center', color=colors)
    ax.set_yticks(y_pos, labels=combustiveis)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Quantidades')
    ax.set_title('Quantidade de medicamentos por Combustível')
    plt.gcf().canvas.manager.set_window_title("Gráfico por Combustível")

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
    print("6. Gráfico de Marcas (Pizza)")
    print("7. Gráfico de Marcas (Colunas Empilhadas)")
    print("8. Gráfico de Combustíveis (Barras)")
    print("9. Finalizar")
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
        grafico()
    elif opcao == 7:
        grafico2()
    elif opcao == 8:
        grafico3()
    else:
        break
