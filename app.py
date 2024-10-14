# Importações
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import json
from secrets import token_hex
from PIL import Image
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cuida+if'
arquivo_usuarios = 'usuarios.json'

# Funções Iniciais para Carregar os Usuários do Json e Salvar os Usuários
def carregar_usuarios():
    with open(arquivo_usuarios, 'r') as arquivo:
        return json.load(arquivo)

def salvar_usuarios(usuarios):
    with open(arquivo_usuarios, 'w', encoding='utf-8') as arquivo:
        json.dump(usuarios, arquivo, indent=4, ensure_ascii=False)

# Rotas Iniciais (Login e Cadastro)
@app.route('/')
def index():
    return render_template('/start/index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('/start/cadastro.html')

# Rota para processar o login
@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("/start/index.html")

    matricula = request.form.get('matricula')
    senha = request.form.get('senha')

    usuarios = carregar_usuarios()

    # Verificar se o usuário é um aluno
    for aluno in usuarios['alunos']:
        if aluno['matricula'] == matricula and aluno['senha'] == senha:
            session['usuario_logado'] = aluno
            session['tipo_usuario'] = 'aluno'  # Adiciona tipo de usuário
            return redirect(url_for('home'))

    # Verificar se o usuário é uma professora
    for professora in usuarios['professoras']:
        if professora['matricula'] == matricula and professora['senha'] == senha:
            session['usuario_logado'] = professora
            session['tipo_usuario'] = 'professora'  # Adiciona tipo de usuário
            return redirect(url_for('home_prof'))

    return render_template('/start/index.html', mensagem="Usuário Inválido!")

# Rota para processar o cadastro
@app.route('/cadastro', methods=['POST'])
def registrar():
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuarios = carregar_usuarios()

    for aluno in usuarios['alunos']:
        if aluno['matricula'] == matricula:
            return render_template('/start/cadastro.html', mensagem="Matrícula já existe!")

    # Adiciona Aluno
    usuarios['alunos'].append({
        "matricula": matricula,
        "nome": nome,
        "email": email,
        "senha": senha,
        "altura": "",
        "peso": "",
        "pressao": "",
        "plano_saude": "",
        "data_nascimento": "",
        "turma": "",
        "curso": "",
        "cidade": "",
        "cep": "",
        "bairro": "",
        "estado": "",
        "rua": "",
        "genero": ""
    })

    salvar_usuarios(usuarios)
    return redirect(url_for('index'))

# Rotas Iniciais dos Alunos
@app.route('/home')
def home():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')

    altura = usuario_logado.get('altura', '') or 'N/A'
    peso = usuario_logado.get('peso', '') or 'N/A'
    pressao = usuario_logado.get('pressao', 'N/A')

    try:
        altura_float = float(altura)
        peso_float = float(peso)
        imc = round(peso_float / (altura_float ** 2), 2) if altura_float > 0 else 'N/A'
    except ValueError:
        imc = 'N/A'

    return render_template('student/home.html', altura=altura, peso=peso, pressao=pressao, imc=imc, nome=usuario_logado['nome'], usuario=usuario_logado)

@app.route('/perfil')
def perfil():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/student/perfil.html', usuario=usuario_logado)

@app.route('/eventos')
def eventos():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/student/eventos.html', usuario=usuario_logado)

@app.route('/avaliacoes')
def avaliacoes():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/student/avaliacoes.html', usuario=usuario_logado)

# Rota para salvar informações do perfil do aluno
@app.route('/perfil', methods=['POST'])
def salvar_perfil():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    perfil_data = {
        "matricula": request.form.get('matricula'),
        "nome": request.form.get('nome'),
        "altura": request.form.get('altura'),
        "peso": request.form.get('peso'),
        "pressao": request.form.get('pressao'),
        "plano_saude": request.form.get('plano_saude'),
        "data_nascimento": request.form.get('data_nascimento'),
        "turma": request.form.get('turma'),
        "curso": request.form.get('curso'),
        "email": request.form.get('email'),
        "cidade": request.form.get('cidade'),
        "cep": request.form.get('cep'),
        "bairro": request.form.get('bairro'),
        "estado": request.form.get('estado'),
        "rua": request.form.get('rua'),
        "genero": request.form.get('genero')
    }

    mensagem = None  # Variável para armazenar a mensagem de erro
    # Verifica se uma nova foto foi enviada
    if 'foto_perfil' in request.files:
        imagem = request.files['foto_perfil']
        if imagem and imagem.filename != '':
            nome_arquivo_imagem = salvar_imagem(imagem)
            if nome_arquivo_imagem:  # Se a imagem foi salva com sucesso
                perfil_data['foto_perfil'] = nome_arquivo_imagem
            else:
                mensagem = "Formato de imagem não permitido. Utilize JPEG ou PNG."  # Armazena a mensagem de erro

    usuarios = carregar_usuarios()
    for usuario in usuarios['alunos']:
        if usuario['matricula'] == perfil_data['matricula']:
            usuario.update(perfil_data)
            break

    salvar_usuarios(usuarios)

    usuario_logado = session['usuario_logado']
    usuario_logado.update(perfil_data)
    session['usuario_logado'] = usuario_logado

    return render_template('/student/perfil.html', usuario=usuario_logado, mensagem=mensagem)

# Rota para salvar informações do perfil da professora
@app.route('/perfil_prof', methods=['POST'])
def salvar_perfil_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    perfil_data = {
        "matricula": request.form.get('matricula'),
        "nome": request.form.get('nome'),
        "data_nascimento": request.form.get('data_nascimento'),
        "email": request.form.get('email'),
        "genero": request.form.get('genero'),
    }

    mensagem = None  # Variável para armazenar a mensagem de erro
    # Verifica se uma nova foto foi enviada
    if 'foto_perfil' in request.files:
        imagem = request.files['foto_perfil']
        if imagem and imagem.filename != '':
            nome_arquivo_imagem = salvar_imagem(imagem)
            if nome_arquivo_imagem:  # Se a imagem foi salva com sucesso
                perfil_data['foto_perfil'] = nome_arquivo_imagem
            else:
                mensagem = "Formato de imagem não permitido. Utilize JPEG ou PNG."  # Armazena a mensagem de erro

    usuarios = carregar_usuarios()
    for usuario in usuarios['professoras']:
        if usuario['matricula'] == perfil_data['matricula']:
            usuario.update(perfil_data)
            break

    salvar_usuarios(usuarios)

    usuario_logado = session['usuario_logado']
    usuario_logado.update(perfil_data)
    session['usuario_logado'] = usuario_logado

    return render_template('/teachers/perfil_prof.html', usuario=usuario_logado, mensagem=mensagem)

# Função para salvar a imagem
def salvar_imagem(imagem):
    extensao = os.path.splitext(imagem.filename)[1].lower()

    if extensao not in ['.jpeg', '.jpg', '.png']:
        return None 

    codigo = token_hex(8)
    nome, _ = os.path.splitext(imagem.filename)  # Ignora a extensão para criar o nome
    nome_arquivo = nome + codigo + extensao
    caminho = os.path.join(app.root_path, "static/fotos_perfil", nome_arquivo)

    imagem_original = Image.open(imagem)

    largura, altura = imagem_original.size
    if largura > altura:
        diferenca = (largura - altura) // 2
        box = (diferenca, 0, largura - diferenca, altura)
    else:
        diferenca = (altura - largura) // 2
        box = (0, diferenca, largura, altura - diferenca)

    imagem_quadrada = imagem_original.crop(box)
    tamanho = (200, 200)
    imagem_quadrada.thumbnail(tamanho)
    imagem_quadrada.save(caminho)

    return nome_arquivo

# Rota apara pegar turma e pegar usuários
def pegar_turmas_cursos():
    usuarios = carregar_usuarios()
    turmas_cursos = {}

    for aluno in usuarios['alunos']:
        turma = aluno.get('turma')
        curso = aluno.get('curso')
        nome = aluno.get('nome')

        if turma and curso:
            chave = f"{turma} - {curso}"
            if chave not in turmas_cursos:
                turmas_cursos[chave] = []
            turmas_cursos[chave].append(nome)

    return turmas_cursos
    
def pegar_todos_usuarios():
    try:
        with open("usuarios.json", 'r', encoding="utf-8") as arquivo:
            usuarios = json.load(arquivo)
    except FileNotFoundError:
        usuarios = []
    return usuarios


# Rotas Iniciais do Professor
@app.route('/home_prof', methods=["POST", "GET"])
def home_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    if request.method == "POST":
        if request.is_json:  # Verifica se é uma requisição AJAX
            data = request.json
            turma = data.get("turma")
            curso = data.get("curso")

            # Pegando todos os usuários
            usuarios = pegar_todos_usuarios()

            # Filtrando os alunos da turma e curso
            usuarios_turma = [
                usuario for usuario in usuarios["alunos"]
                if usuario["curso"] == curso and usuario["turma"] == turma
            ]

            # Retorna os dados como JSON
            return jsonify(usuarios_turma=usuarios_turma)

        return redirect(url_for('home_prof'))

    else:
        usuario_logado = session.get('usuario_logado')
        turmas_cursos = pegar_turmas_cursos()  # Função que carrega turmas e cursos

        return render_template('/teachers/home_prof.html', usuario=usuario_logado, turmas_cursos=turmas_cursos)

@app.route('/perfil_prof')
def perfil_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/teachers/perfil_prof.html', usuario=usuario_logado)

@app.route('/eventos_prof')
def eventos_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/teachers/eventos_prof.html', usuario=usuario_logado)

@app.route('/avaliacoes_prof')
def avaliacoes_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/teachers/avaliacoes_prof.html', usuario=usuario_logado)

# Rota para sair da sessão
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
