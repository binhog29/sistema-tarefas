document.addEventListener('DOMContentLoaded', () => {
    const formAdicionar = document.getElementById('form-adicionar-ajax');
    const listaTarefas = document.getElementById('lista-tarefas');
    const novaTarefaInput = document.getElementById('nova-tarefa');

    formAdicionar.addEventListener('submit', (e) => {
        e.preventDefault();
        const tarefa = novaTarefaInput.value.trim();
        if (!tarefa) return;

        fetch('/adicionar-ajax', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: tarefa=${encodeURIComponent(tarefa)}
        })
        .then(response => response.json())
        .then(data => {
            const li = document.createElement('li');
            li.className = 'tarefa';
            li.dataset.id = data.id;
            li.innerHTML = `
                ${data.descricao}
                <div class="actions">
                    <a href="/editar/${data.id}">Editar</a>
                    <a href="/deletar/${data.id}" onclick="return confirm('Tem certeza que quer deletar?')">Deletar</a>
                </div>
            `;
            listaTarefas.appendChild(li);
            novaTarefaInput.value = '';
        })
        .catch(error => console.error('Erro ao adicionar tarefa:', error));
    });
});