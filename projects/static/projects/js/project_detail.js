let converter;
let newSectionCounter = 0;

function createElementFromHTML(htmlString) {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleEdit(sectionId) {
    const displayDiv = document.getElementById(`section-display-${sectionId}`);
    const editDiv = document.getElementById(`section-edit-${sectionId}`);
    const titleDisplayDiv = document.getElementById(`section-title-display-${sectionId}`);
    const titleEditDiv = document.getElementById(`section-title-edit-${sectionId}`);
    
    const currentCard = document.getElementById(`section-${sectionId}`);
    
    if (displayDiv && editDiv && titleDisplayDiv && titleEditDiv) {
        if (displayDiv.classList.contains('hidden')) {
            displayDiv.classList.remove('hidden');
            titleDisplayDiv.classList.remove('hidden');
            editDiv.classList.remove('active');
            titleEditDiv.classList.remove('active');
            
            if (currentCard) {
                currentCard.classList.remove('editing-mode');
            }
        } else {
            displayDiv.classList.add('hidden');
            titleDisplayDiv.classList.add('hidden');
            editDiv.classList.add('active');
            titleEditDiv.classList.add('active');
            
            if (currentCard) {
                currentCard.classList.add('editing-mode');
            }
            
            const textArea = editDiv.querySelector('textarea');
            if (textArea) {
                setTimeout(() => {
                    textArea.focus();
                    const length = textArea.value.length;
                    textArea.setSelectionRange(length, length);
                }, 50);
            }
        }
    }
}

function editDescription() {
    const descDisplay = document.getElementById('project-description-display');
    const container = document.getElementById('project-description-container');
    const editBtn = document.getElementById('edit-desc-btn');
    
    if (!descDisplay || !container) return;
    
    const currentDesc = descDisplay.innerText;

    if (editBtn) editBtn.style.display = 'none';

    const textarea = document.createElement('textarea');
    textarea.className = 'form-control form-control-sm small mb-2';
    textarea.rows = 5;
    textarea.value = currentDesc;
    textarea.style.lineHeight = '1.5';
    textarea.style.fontSize = '0.875rem';

    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'd-flex gap-1 justify-content-end';
    actionsDiv.innerHTML = `
        <button type="button" class="btn btn-sm btn-primary rounded-pill px-3" id="save-desc-btn" style="font-size: 0.75rem;">Salvar</button>
        <button type="button" class="btn btn-sm btn-secondary rounded-pill px-2" id="cancel-desc-btn" style="font-size: 0.75rem;">Cancelar</button>
    `;

    function cancelEditing() {
        container.innerHTML = '';
        container.appendChild(descDisplay);
        if (editBtn) editBtn.style.display = 'inline-block';
    }

    function submitNewDescription() {
        const newValue = textarea.value.trim();
        if (newValue !== currentDesc) {
            const hiddenTextarea = document.getElementById('description-value');
            hiddenTextarea.value = newValue;
            hiddenTextarea.form.submit();
        } else {
            cancelEditing();
        }
    }

    container.innerHTML = '';
    container.appendChild(textarea);
    container.appendChild(actionsDiv);
    
    textarea.focus();

    document.getElementById('save-desc-btn').addEventListener('click', submitNewDescription);
    document.getElementById('cancel-desc-btn').addEventListener('click', cancelEditing);

    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            cancelEditing();
        }
    });
}

function editTitle() {
    const titleHeader = document.getElementById('project-title-display');
    const currentTitle = titleHeader.innerText;
    const editBtn = document.getElementById('edit-title-btn');

    if (editBtn) editBtn.style.display = 'none';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control form-control-lg fw-bold mb-3';
    input.value = currentTitle;
    input.style.fontSize = '2.5rem';

    titleHeader.parentNode.replaceChild(input, titleHeader);
    input.focus();

    function submitNewTitle() {
        const newValue = input.value.trim();
        if (newValue && newValue !== currentTitle) {
            document.getElementById('title-value').value = newValue;
            document.getElementById('title-value').form.submit();
        } else {
            input.parentNode.replaceChild(titleHeader, input);
            if (editBtn) editBtn.style.display = 'inline-block';
        }
    }

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            submitNewTitle();
        }
        if (e.key === 'Escape') {
            input.parentNode.replaceChild(titleHeader, input);
            if (editBtn) editBtn.style.display = 'inline-block';
        }
    });

    input.addEventListener('blur', function() {
        submitNewTitle();
    });
}

function addNewSection() {
    newSectionCounter++;
    const tempId = `temp-${Date.now()}-${newSectionCounter}`;
    const sectionsContainer = document.getElementById('sections-container');
    const addButton = document.querySelector('.add-section-btn');
    const emptyMessage = document.querySelector('.empty-state');
    
    if (addButton) addButton.classList.add('d-none');
    if (emptyMessage) emptyMessage.classList.add('d-none');
    
    const newSectionHtml = `
        <div class="section-card" id="section-${tempId}" data-temp-id="${tempId}">
            <div class="section-header mb-3">
                <h3 class="mb-0">Nova Seção</h3>
            </div>

            <div id="section-edit-${tempId}" class="inline-edit active">
                <div class="mb-2">
                    <label class="form-label small fw-bold text-muted">Tipo de Conteúdo (Tag):</label>
                    <select id="section-type-${tempId}" class="form-select form-select-sm" onchange="updateFormHint('${tempId}')">
                        <option value="text">Texto Simples</option>
                        <option value="question">Pergunta / Dúvida</option>
                        <option value="reference">Referência / Link</option>
                    </select>
                </div>

                <div class="mb-2">
                    <label class="form-label small fw-bold text-muted">Título:</label>
                    <input type="text" id="section-title-${tempId}" class="form-control" value="Nova Seção">
                </div>

                <div class="mb-2">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <label class="form-label small fw-bold text-muted mb-0">Conteúdo:</label>
                        <button type="button" class="btn btn-xs btn-outline-secondary py-0 px-2 small" style="font-size: 0.75rem;" onclick="insertCodeSnippet('section-content-${tempId}')">
                            + Inserir Bloco de Código
                        </button>
                    </div>
                    <textarea id="section-content-${tempId}" class="form-control" rows="8" placeholder="Escreva aqui..."></textarea>
                </div>

                <small id="hint-${tempId}" class="text-muted d-block mb-3"><b>Markdown suportado:</b> títulos, listas, código e links.</small>
                
                <button class="btn btn-sm btn-primary" onclick="saveNewSection('${tempId}')">Salvar</button>
                <button class="btn btn-sm btn-secondary" onclick="deleteTempSection('${tempId}')">Cancelar</button>
            </div>
        </div>
    `;
    
    if (addButton) {
        sectionsContainer.insertBefore(createElementFromHTML(newSectionHtml), addButton);
    } else {
        sectionsContainer.insertAdjacentHTML('afterbegin', newSectionHtml);
    }
    
    document.getElementById(`section-title-${tempId}`).focus();
}

function saveNewSection(tempId) {
    const title = document.getElementById(`section-title-${tempId}`).value;
    const content = document.getElementById(`section-content-${tempId}`).value;
    const sectionType = document.getElementById(`section-type-${tempId}`).value;
    
    const container = document.getElementById('sections-container');
    const username = container.getAttribute('data-owner-username');
    const slug = container.getAttribute('data-project-slug');
    
    fetch(`/${username}/${slug}/section/create/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'title=' + encodeURIComponent(title) + '&content=' + encodeURIComponent(content) + '&section_type=' + encodeURIComponent(sectionType)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao salvar seção: ' + (data.error || 'Erro desconhecido.'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erro de comunicação com o servidor.');
    });
}

function deleteTempSection(tempId) {
    const tempSection = document.getElementById(`section-${tempId}`);
    if (tempSection) {
        tempSection.remove();
    }
    
    const addButton = document.querySelector('.add-section-btn');
    const emptyMessage = document.querySelector('.empty-state');

    if (addButton) {
        addButton.classList.remove('d-none');
    }
    if (emptyMessage) {
        const remainingCards = document.querySelectorAll('#sections-container .section-card');
        if (remainingCards.length === 0) {
            emptyMessage.classList.remove('d-none');
        }
    }
}

function insertCodeSnippet(textareaId) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const textBefore = textarea.value.substring(0, startPos);
    const textAfter = textarea.value.substring(endPos, textarea.value.length);
    
    const selectedText = textarea.value.substring(startPos, endPos) || "// insira seu código aqui";
    const snippet = `\`\`\`linguagem\n${selectedText}\n\`\`\``;

    textarea.value = textBefore + snippet + textAfter;
    
    textarea.focus();
    const newCursorPos = startPos + snippet.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);
}

function updateFormHint(tempId) {
    const type = document.getElementById(`section-type-${tempId}`).value;
    const hintElement = document.getElementById(`hint-${tempId}`);
    const textarea = document.getElementById(`section-content-${tempId}`);
    
    if (type === 'question') {
        hintElement.innerHTML = "<b>Modo Pergunta:</b> Usuários poderão responder e criar discussões específicas para sanar essa dúvida.";
        textarea.placeholder = "Qual a melhor abordagem para...";
    } else if (type === 'reference') {
        hintElement.innerHTML = "<b>Modo Referência:</b> Adicione links úteis no formato Markdown: <code class='text-dark'>[Nome do Site](https://link.com)</code> acompanhado de descrições.";
        textarea.placeholder = "- [Documentação Oficial](https://...)";
    } else {
        hintElement.innerHTML = "<b>Markdown suportado:</b> títulos, listas, código e links.";
        textarea.placeholder = "Escreva aqui...";
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof markdownit !== 'undefined') {
        converter = markdownit({
            html: true,
            linkify: true,
            typographer: true,
            highlight: function(str, lang) {
                return '<pre class="hljs"><code>' + markdownit().utils.escapeHtml(str) + '</code></pre>';
            }
        });
        
        document.querySelectorAll('.markdown-content').forEach(function(element) {
            const markdown = element.getAttribute('data-markdown');
            if (markdown) {
                element.innerHTML = converter.render(markdown);
            }
        });
    }
    
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach(function(block) {
            hljs.highlightElement(block);
        });
    }
});