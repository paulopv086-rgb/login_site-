import os
import json
import uuid6 # type: ignore
import webbrowser
from threading import Timer
from flask import Flask, jsonify, render_template, request, session, redirect, url_for # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from traducoes import TEXTOS

app = Flask(__name__)

# Chave secreta única usando UUID v7
app.secret_key = str(uuid6.uuid7())

# 🛡️ Sistema de Limite de Tentativas (Rate Limiting)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

arquivo_banco = "banco_dados.json"

# Garante que o arquivo JSON existe ao iniciar
if not os.path.exists(arquivo_banco):
    with open(arquivo_banco, 'w', encoding='utf-8') as f:
        json.dump({"usuarios_salvos": []}, f, indent=4)


@app.route('/')
def pagina_inicial():
    idioma = request.args.get('lang', default='pt')
    palavras_pagina = TEXTOS.get(idioma, TEXTOS['pt'])
    usuario_logado = session.get('usuario')
    
    # Nome do arquivo corrigido para 'estrutura.html'
    return render_template('estruture.html', usuario=usuario_logado, t=palavras_pagina, idioma_atual=idioma)


@app.route('/api/dados', methods=['POST'])
def pagina_dados():
    idioma = request.args.get('lang', default='pt')
    palavras_pagina = TEXTOS.get(idioma, TEXTOS['pt'])

    # Coleta dados usando POST para não expor na URL
    usuario = request.form.get('nome_usuario', default='Visitante').strip()
    idade = request.form.get('idade', default='Nao informada')
    email = request.form.get('email', default='Nao informado')
    senha = request.form.get('senha', default='')

    with open(arquivo_banco, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Validação de usuário duplicado
    for registro in dados["usuarios_salvos"]:
        if usuario.lower() == registro["usuario_save"].lower():
            return render_template('error409.html', t=palavras_pagina), 409

    # 🔒 Salva a senha usando HASH criptografado
    senha_criptografada = generate_password_hash(senha)

    dicionario_usuario = {
        "usuario_save": usuario,
        "idade_save": idade,
        "email_save": email,
        "senha_save": senha_criptografada
    }
    dados["usuarios_salvos"].append(dicionario_usuario)

    with open(arquivo_banco, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

    return jsonify({"status": "sucesso", "mensagem": "Usuario cadastrado com sucesso!"})

@app.route('/login', methods=['GET', 'POST'])
# 🛡️ O segredo está aqui: methods=["POST"] garante que só envios de formulário contam!
@limiter.limit("5 per minute", methods=["POST"])  
def tela_login():
    idioma = request.args.get('lang', default='pt')
    palavras_pagina = TEXTOS.get(idioma, TEXTOS['pt'])

    # Quando a pessoa clica no botão "Entrar" (envio real do formulário)
    if request.method == 'POST':
        nome_digitado = request.form.get('usuario', default='').strip()
        senha_digitada = request.form.get('senha', default='')

        with open(arquivo_banco, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        for registro in dados['usuarios_salvos']:
            if nome_digitado.lower() == registro['usuario_save'].lower():
                # Confere a senha criptografada
                if check_password_hash(registro['senha_save'], senha_digitada):
                    session['usuario'] = registro['usuario_save']
                    return redirect(url_for('pagina_depois'))

        # Se errou o usuário ou a senha, cai aqui e a tentativa POST é contabilizada!
        return 'Usuário ou senha incorretos. <a href="/login">Tente novamente</a>.', 401

    # Se a pessoa só abriu ou atualizou a página (método GET), entrega o HTML normal sem gastar o limite
    return render_template('login.html', t=palavras_pagina, idioma_atual=idioma)



@app.route('/parabens')
def pagina_depois():
    if 'usuario' not in session:
        return redirect(url_for('tela_login'))
    return render_template('fez_login.html')


@app.route('/error409')
def pagina_error():
    idioma = request.args.get('lang', default='pt')
    palavras_pagina = TEXTOS.get(idioma, TEXTOS['pt'])
    return render_template('error409.html', t=palavras_pagina), 409


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pagina_inicial'))


@app.errorhandler(429)
def limite_excedido(e):
    return "Muitas tentativas de login! Aguarde um minuto e tente novamente.", 429


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
