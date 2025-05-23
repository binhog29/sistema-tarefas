from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)  # Corrigido aqui!

def get_db_connection():
    conn = sqlite3.connect('tarefas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    tarefas = conn.execute('SELECT * FROM tarefas').fetchall()
    conn.close()
    return render_template('index.html', tarefas=tarefas)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        tarefa = request.form['tarefa']
        conn = get_db_connection()
        conn.execute("INSERT INTO tarefas (descricao, concluida) VALUES (?, 0)", (tarefa,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/concluir/<int:id>')
def concluir(id):
    conn = get_db_connection()
    conn.execute("UPDATE tarefas SET concluida = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        concluida BOOLEAN DEFAULT 0
    )''')
    conn.close()
    app.run(debug=True)