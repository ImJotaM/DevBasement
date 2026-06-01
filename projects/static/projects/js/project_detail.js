let converter;
let newSectionCounter = 0;
let draggedItem = null;
let reorderTimeout;

let scrollSpeed = 0;
let scrollAnimationFrame = null;

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
                currentCard.setAttribute('draggable', 'false');
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

function editTitle() {
    const currentTitle = document.getElementById('title-value').value;
    const newTitle = prompt('Editar título do projeto:', currentTitle);
    if (newTitle && newTitle !== currentTitle) {
        document.getElementById('title-value').value = newTitle;
        document.querySelector('#title-value').closest('form').submit();
    }
}

function addNewSection() {
    newSectionCounter++;
    const tempId = `temp-${Date.now()}-${newSectionCounter}`;
    const sectionsContainer = document.getElementById('sections-container');
    const addButton = document.querySelector('.add-section-btn');
    const emptyMessage = document.getElementById('empty-message');
    
    if (addButton) {
        addButton.classList.add('d-none');
    }
    if (emptyMessage) {
        emptyMessage.classList.add('d-none');
    }
    
    const newSectionHtml = `
        <div class="section-card" id="section-${tempId}" data-temp-id="${tempId}">
            <div class="section-header">
                <div class="d-flex align-items-center gap-2">
                    <div>
                        <h3 class="mb-0">Nova Seção</h3>
                    </div>
                </div>
            </div>

            <div id="section-display-${tempId}" class="inline-display hidden">
                <div class="markdown-content"></div>
            </div>

            <div id="section-edit-${tempId}" class="inline-edit active">
                <input type="text" id="section-title-${tempId}" class="form-control mb-2" value="Nova Seção">
                <textarea id="section-content-${tempId}" class="form-control mb-2" rows="10">Escreva o conteúdo da sua seção aqui...</textarea>
                <small class="text-muted d-block mb-2">Markdown suportado: títulos, listas, código, links, etc.</small>
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
    const projectId = document.getElementById('sections-container').getAttribute('data-project-id');
    
    fetch(`/projects/${projectId}/section/create/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'title=' + encodeURIComponent(title) + '&content=' + encodeURIComponent(content)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function deleteTempSection(tempId) {
    const tempSection = document.getElementById(`section-${tempId}`);
    if (tempSection) {
        tempSection.remove();
    }
    
    const addButton = document.querySelector('.add-section-btn');
    const emptyMessage = document.getElementById('empty-message');

    if (addButton) {
        addButton.classList.remove('d-none');
    }
    if (emptyMessage) {
        emptyMessage.classList.remove('d-none');
    }
}

function handleAutoScroll() {
    if (scrollSpeed !== 0) {
        window.scrollBy(0, scrollSpeed);
        scrollAnimationFrame = requestAnimationFrame(handleAutoScroll);
    } else {
        scrollAnimationFrame = null;
    }
}

function initDragAndDrop() {
    const container = document.getElementById('sections-container');
    if (!container) return;

    const cards = container.querySelectorAll('.section-card');
    
    cards.forEach(card => {
        const handle = card.querySelector('.drag-handle');
        if (!handle) return;

        card.setAttribute('draggable', 'false');
        
        handle.addEventListener('mousedown', () => {
            if (!card.classList.contains('editing-mode') && !card.classList.contains('pinned')) {
                card.setAttribute('draggable', 'true');
            }
        });
        
        handle.addEventListener('mouseup', () => {
            card.setAttribute('draggable', 'false');
        });

        card.addEventListener('dragstart', (e) => {
            if (card.classList.contains('editing-mode') || card.classList.contains('pinned')) {
                e.preventDefault();
                return false;
            }
            draggedItem = card;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
            card.setAttribute('draggable', 'false');
            
            const activeDragOvers = document.querySelectorAll('.section-card.drag-over');
            activeDragOvers.forEach(c => c.classList.remove('drag-over'));
            
            draggedItem = null;
            
            scrollSpeed = 0;
            if (scrollAnimationFrame) {
                cancelAnimationFrame(scrollAnimationFrame);
                scrollAnimationFrame = null;
            }
        });

        card.addEventListener('dragover', (e) => {
            e.preventDefault();
            
            if (card !== draggedItem && !card.classList.contains('editing-mode') && !card.classList.contains('pinned')) {
                card.classList.add('drag-over');
            }

            const threshold = 140;
            const maxSpeed = 16;
            const mouseY = e.clientY;
            const viewHeight = window.innerHeight;

            if (mouseY < threshold) {
                scrollSpeed = -Math.max(4, Math.round((1 - mouseY / threshold) * maxSpeed));
                if (!scrollAnimationFrame) {
                    scrollAnimationFrame = requestAnimationFrame(handleAutoScroll);
                }
            } else if (mouseY > viewHeight - threshold) {
                const distanceToBottom = viewHeight - mouseY;
                scrollSpeed = Math.max(4, Math.round((1 - distanceToBottom / threshold) * maxSpeed));
                if (!scrollAnimationFrame) {
                    scrollAnimationFrame = requestAnimationFrame(handleAutoScroll);
                }
            } else {
                scrollSpeed = 0;
            }
        });

        card.addEventListener('dragleave', () => {
            card.classList.remove('drag-over');
        });

        card.addEventListener('drop', (e) => {
            e.preventDefault();
            card.classList.remove('drag-over');

            if (card.classList.contains('editing-mode') || card.classList.contains('pinned')) return;

            if (draggedItem && card !== draggedItem) {
                const allCards = Array.from(container.querySelectorAll('.section-card'));
                const draggedIndex = allCards.indexOf(draggedItem);
                const targetIndex = allCards.indexOf(card);

                if (draggedIndex < targetIndex) {
                    container.insertBefore(draggedItem, card.nextSibling);
                } else {
                    container.insertBefore(draggedItem, card);
                }
                saveOrder();
            }
        });
    });
}

function saveOrder() {
    clearTimeout(reorderTimeout); 

    reorderTimeout = setTimeout(() => {
        const container = document.getElementById('sections-container');
        const projectId = container.getAttribute('data-project-id');
        const cards = container.querySelectorAll('.section-card');
        
        const sectionIds = Array.from(cards)
            .map(card => card.getAttribute('data-section-id'))
            .filter(id => id !== null);

        fetch(`/projects/${projectId}/section/reorder/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ section_ids: sectionIds })
        });
    }, 500);
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

    initDragAndDrop();
});