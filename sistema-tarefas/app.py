from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tarefas.db')
    # Cria tabela categorias
    conn.execute('''CREATE TABLE IF NOT EXISTS categorias 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nome TEXT)''')
    # Cria tabela tarefas
    conn.execute('''CREATE TABLE IF NOT EXISTS tarefas 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    descricao TEXT, 
                    concluida INTEGER, 
                    categoria_id INTEGER, 
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id))''')
    # Adiciona categorias padrão
    conn.execute('INSERT OR IGNORE INTO categorias (id, nome) VALUES (1, "Estudos")')
    conn.execute('INSERT OR IGNORE INTO categorias (id, nome) VALUES (2, "Trabalho")')
    conn.execute('INSERT OR IGNORE INTO categorias (id, nome) VALUES (3, "Pessoal")')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('tarefas.db')
    cursor = conn.execute('SELECT id, nome FROM categorias')
    categorias = [{'id': row[0], 'nome': row[1]} for row in cursor]
    cursor = conn.execute('''SELECT t.id, t.descricao, t.concluida, c.nome 
                           FROM tarefas t 
                           LEFT JOIN categorias c ON t.categoria_id = c.id''')
    tarefas = [{'id': row[0], 'descricao': row[1], 'concluida': row[2], 'categoria': row[3]} for row in cursor]
    conn.close()
    return render_template('index.html', tarefas=tarefas, categorias=categorias)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    descricao = request.form['descricao']
    categoria_id = int(request.form['categoria_id'])
    conn = sqlite3.connect('tarefas.db')
    conn.execute('INSERT INTO tarefas (descricao, concluida, categoria_id) VALUES (?, 0, ?)', 
                (descricao, categoria_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/concluir/<int:id>')
def concluir(id):
    conn = sqlite3.connect('tarefas.db')
    conn.execute('UPDATE tarefas SET concluida = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)