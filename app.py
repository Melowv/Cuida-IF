from flask import Flask, request, render_template, redirect, url_for, session
import json
from secrets import token_hex
from PIL import Image
import os

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

    usuarios = carregar_usuarios()

    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == matricula:
            return render_template('/start/cadastro.html', mensagem="Matrícula já existe!")

    # Adicionar usuário com dados básicos
    usuarios['usuarios'].append({
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

# Rota para processar o login
@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("/start/index.html")

    matricula = request.form.get('matricula')
    senha = request.form.get('senha')

    # Verifica se as credenciais são válidas
    usuarios = carregar_usuarios()
    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == matricula and usuario['senha'] == senha:
            session['usuario_logado'] = usuario
            return redirect(url_for('home'))

    return render_template('/start/index.html', mensagem="Usuário Inválido!")

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

# Rotas Iniciais do Professor
@app.route('/home_prof')
def home_prof():
    if not session.get('usuario_logado'):
        return redirect(url_for('index'))

    usuario_logado = session.get('usuario_logado')
    return render_template('/teachers/home_prof.html', usuario=usuario_logado)

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

# Rota para salvar informações do perfil
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

    # Verifica se uma nova foto foi enviada
    if 'foto_perfil' in request.files:
        imagem = request.files['foto_perfil']
        if imagem and imagem.filename != '':
            nome_arquivo_imagem = salvar_imagem(imagem)
            perfil_data['foto_perfil'] = nome_arquivo_imagem

    usuarios = carregar_usuarios()
    for usuario in usuarios['usuarios']:
        if usuario['matricula'] == perfil_data['matricula']:
            usuario.update(perfil_data)
            break

    salvar_usuarios(usuarios)

    # Atualiza a sessão com os dados mais recentes
    usuario_logado = session['usuario_logado']
    usuario_logado.update(perfil_data)
    session['usuario_logado'] = usuario_logado

    return redirect(url_for('perfil'))


# Função para salvar a imagem
def salvar_imagem(imagem):
    codigo = token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
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

# Rota para desconectar
@app.route('/logout')
def logout():
    del session['usuario_logado']
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
