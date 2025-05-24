from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aleatoria'  # Substitua por uma chave segura

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe de usuário pro Flask-Login


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @property
    def username(self):
        conn = get_db_connection()
        user = conn.execute(
            'SELECT username FROM usuarios WHERE id = ?', (self.id,)).fetchone()
        conn.close()
        return user['username'] if user else None


@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if not user:
            print(f"Usuário com ID {user_id} não encontrado.")
            return None
        print(
            f"Usuário encontrado: ID {user['id']}, Username: {user['username']}")
        return User(user['id'])
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None


def get_db_connection():
    conn = sqlite3.connect('tarefas.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    filtro = request.args.get('filtro', 'todas')
    if filtro == 'concluidas':
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE concluida = 1 AND usuario_id = ?', (current_user.id,)).fetchall()
    elif filtro == 'pendentes':
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE concluida = 0 AND usuario_id = ?', (current_user.id,)).fetchall()
    else:
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE usuario_id = ?', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', tarefas=tarefas, filtro=filtro)


@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar():
    if request.method == 'POST':
        tarefa = request.form['tarefa']
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tarefas (descricao, concluida, usuario_id) VALUES (?, 0, ?)", (tarefa, current_user.id))
        conn.commit()
        conn.close()
        flash('Tarefa adicionada com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('adicionar.html')


@app.route('/adicionar-ajax', methods=['POST'])
@login_required
def adicionar_ajax():
    tarefa = request.form['tarefa']
    conn = get_db_connection()
    conn.execute("INSERT INTO tarefas (descricao, concluida, usuario_id) VALUES (?, 0, ?)",
                 (tarefa, current_user.id))
    conn.commit()
    tarefa_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    nova_tarefa = conn.execute(
        "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)).fetchone()
    conn.close()
    return jsonify({'id': nova_tarefa['id'], 'descricao': nova_tarefa['descricao'], 'concluida': nova_tarefa['concluida']})


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    conn = get_db_connection()
    tarefa = conn.execute(
        'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?', (id, current_user.id)).fetchone()
    if not tarefa:
        flash('Tarefa não encontrada ou não pertence a você!', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        nova_descricao = request.form['tarefa']
        concluida = 1 if 'concluida' in request.form else 0
        conn.execute('UPDATE tarefas SET descricao = ?, concluida = ? WHERE id = ?',
                     (nova_descricao, concluida, id))
        conn.commit()
        conn.close()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('index'))
    conn.close()
    return render_template('editar.html', tarefa=tarefa)


@app.route('/deletar/<int:id>')
@login_required
def deletar(id):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM tarefas WHERE id = ? AND usuario_id = ?', (id, current_user.id))
    conn.commit()
    conn.close()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            login_user(User(user['id']))
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Usuário ou senha incorretos!', 'error')
    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Usuário já existe!', 'error')
            conn.close()
            return redirect(url_for('cadastro'))
        conn.execute(
            'INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Usuário cadastrado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Limpa a sessão ao fazer logout
    flash('Você saiu da sua conta!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        concluida BOOLEAN DEFAULT 0,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )''')
    conn.commit()
    conn.close()
    app.run(debug=True)
