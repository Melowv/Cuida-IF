from flask import Flask, request, render_template, redirect, url_for, session
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cuida+if'

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
    return render_template('/start/index.html')

# Rota para a página de cadastro

@app.route('/cadastro')
def cadastro():
    return render_template('/start/cadastro.html')

# Rota para processar o cadastro

@app.route('/cadastro', methods=['POST'])
def registrar():
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not matricula or not nome or not email or not senha:
        return render_template('/start/cadastro.html', mensagem="Todos os campos são obrigatórios!")

    usuarios = carregar_usuarios()

    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == matricula:
            return render_template('/start/cadastro.html', mensagem="Matrícula já existe!")

    usuarios['usuarios'].append({
        "matricula": matricula,
        "nome": nome,
        "email": email,
        "senha": senha
    })
    
    salvar_usuarios(usuarios)
    return redirect(url_for('index'))

# Rota para processar o login

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        render_template("/start/index.html")

    matricula = request.form.get('matricula')
    senha = request.form.get('senha')

    if not matricula or not senha:
        return render_template('/start/index.html', mensagem="Preencha todos os campos!")

    usuarios = carregar_usuarios()

    # Verifica se as credenciais são válidas
    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == '20201461' and usuario['senha'] == '1234':
            session['usuario_logado'] = usuario
            return redirect(url_for('professor'))
    
        elif usuario['matricula'] == matricula and usuario['senha'] == senha:
            session['usuario_logado'] = usuario
            return redirect(url_for('home'))
        
    return render_template('/start/index.html', mensagem="Usuário Inválido!")

# Rotas Iniciais

@app.route('/home')
def home():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    nome_usuario = usuario_logado['nome']

    return render_template('/student/home.html', nome = nome_usuario)

@app.route('/perfil')
def perfil():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    nome_usuario = usuario_logado['nome']

    return render_template('/student/perfil.html', nome = nome_usuario)
    
@app.route('/eventos')
def eventos():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    nome_usuario = usuario_logado['nome']

    return render_template('/student/eventos.html', nome = nome_usuario)
    
@app.route('/avaliacoes')
def avaliacoes():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    nome_usuario = usuario_logado['nome']

    return render_template('/student/avaliacoes.html', nome = nome_usuario)

# Rotas Professor

@app.route('/professor')
def professor():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    nome_usuario = usuario_logado['nome']

    return render_template('/teachers/professor.html', nome = nome_usuario)

# Rota para desconectar

@app.route('/logout')
def logout():
    del session['usuario_logado']
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)