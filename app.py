from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)

# Caminho para o arquivo JSON que armazena os usuários
arquivo_usuarios = 'usuarios.json'

# Função para carregar os usuários do arquivo JSON
def carregar_usuarios():
    with open(arquivo_usuarios, 'r') as arquivo:
        return json.load(arquivo)

# Função para salvar os usuários no arquivo JSON
def salvar_usuarios(usuarios):
    with open(arquivo_usuarios, 'w') as arquivo:
        json.dump(usuarios, arquivo, indent=4)

# Rota para a página inicial (login)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para processar o cadastro
@app.route('/cadastro', methods=['POST'])
def registrar():
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not matricula or not nome or not email or not senha:
        return render_template('cadastro.html', mensagem="Todos os campos são obrigatórios!")

    usuarios = carregar_usuarios()

    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == matricula:
            return render_template('cadastro.html', mensagem="Matrícula já existe!")

    usuarios['usuarios'].append({
        "matricula": matricula,
        "nome": nome,
        "email": email,
        "senha": senha
    })
    
    salvar_usuarios(usuarios)

    return render_template('index.html', mensagem="Cadastro realizado com sucesso!")

# Rota para processar o login
@app.route('/login', methods=['POST'])
def login():
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')

    if not matricula or not senha:
        return render_template('index.html', mensagem="Preencha todos os campos!")

    usuarios = carregar_usuarios()

    # Verifica se as credenciais são válidas
    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == matricula and usuario['senha'] == senha:
            return render_template('inicio.html')

    return render_template('index.html', mensagem="Usuário Inválido!")

if __name__ == '__main__':
    app.run(debug=True)