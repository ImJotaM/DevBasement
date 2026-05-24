let converter;
let draggedItem = null;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof markdownit !== 'undefined') {
        converter = markdownit({
            html: true,
            linkify: true,
            typographer: true,
            highlight: function(str, lang) {
                return '<pre class="hljs"><code>' + converter.utils.escapeHtml(str) + '</code></pre>';
            }
        });
        
        document.querySelectorAll('.markdown-content').forEach(function(element) {
            const markdown = element.getAttribute('data-markdown');
            if (markdown) {
                element.innerHTML = converter.render(markdown);
            }
        });
    }
    
    initDragAndDrop();
});

function initDragAndDrop() {
    const sectionsContainer = document.getElementById('sections-container');
    if (!sectionsContainer) return;
    
    const sections = sectionsContainer.querySelectorAll('.section-card');
    sections.forEach(section => {
        const dragHandle = section.querySelector('.drag-handle');
        if (!dragHandle) return;
        
        const newDragHandle = dragHandle.cloneNode(true);
        dragHandle.parentNode.replaceChild(newDragHandle, dragHandle);
        
        newDragHandle.addEventListener('dragstart', function(e) {
            draggedItem = section;
            section.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', section.id);
        });
        
        newDragHandle.addEventListener('dragend', function(e) {
            section.classList.remove('dragging');
            document.querySelectorAll('.section-card').forEach(s => {
                s.classList.remove('drag-over');
            });
            draggedItem = null;
        });
        
        section.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            if (section !== draggedItem) {
                section.classList.add('drag-over');
            }
        });
        
        section.addEventListener('dragenter', function(e) {
            e.preventDefault();
            if (section !== draggedItem) {
                section.classList.add('drag-over');
            }
        });
        
        section.addEventListener('dragleave', function(e) {
            if (!section.contains(e.relatedTarget)) {
                section.classList.remove('drag-over');
            }
        });
        
        section.addEventListener('drop', function(e) {
            e.preventDefault();
            section.classList.remove('drag-over');
            
            if (draggedItem && section !== draggedItem) {
                const container = sectionsContainer;
                const draggedIndex = Array.from(container.children).indexOf(draggedItem);
                const targetIndex = Array.from(container.children).indexOf(section);
                
                if (draggedIndex < targetIndex) {
                    section.parentNode.insertBefore(draggedItem, section.nextSibling);
                } else {
                    section.parentNode.insertBefore(draggedItem, section);
                }
                
                saveOrder(container);
            }
        });
        
        section.setAttribute('draggable', 'false');
        newDragHandle.setAttribute('draggable', 'true');
    });
}

function saveOrder(container) {
    const sectionIds = Array.from(container.querySelectorAll('.section-card')).map(card => 
        parseInt(card.getAttribute('data-section-id'))
    );
    
    const projectId = document.getElementById('sections-container').getAttribute('data-project-id');
    
    fetch(`/projects/${projectId}/section/reorder/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ section_ids: sectionIds })
    });
}

function createNewSection(projectId) {
    fetch(`/projects/${projectId}/section/create/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'title=Nova Seção&content=Escreva o conteúdo da sua seção aqui...'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const sectionsContainer = document.getElementById('sections-container');
            const addButton = sectionsContainer.querySelector('.add-section-btn');
            
            const newSectionHtml = `
                <div class="section-card" id="section-${data.section_id}" data-section-id="${data.section_id}">
                    <div class="section-header">
                        <div class="d-flex align-items-center gap-2">
                            <i class="fas fa-grip-vertical drag-handle"></i>
                            <div id="section-title-display-${data.section_id}">
                                <h3 class="mb-0">${escapeHtml(data.title)}</h3>
                            </div>
                        </div>
                        <div>
                            <button class="pin-btn" onclick="togglePinSection(${data.section_id})" title="Fixar/Desfixar">
                                <i class="fas fa-thumbtack"></i>
                            </button>
                            <button class="edit-btn me-2" onclick="editSection(${data.section_id})" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="delete-btn" onclick="deleteSection(${data.section_id})" title="Excluir">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div id="section-display-${data.section_id}" class="inline-display hidden">
                        <div id="section-content-display-${data.section_id}" class="markdown-content" data-markdown="${escapeHtml(data.content)}">
                            ${escapeHtml(data.content).replace(/\n/g, '<br>')}
                        </div>
                    </div>

                    <div id="section-edit-${data.section_id}" class="inline-edit active">
                        <input type="text" id="section-title-${data.section_id}" class="form-control mb-2" value="${escapeHtml(data.title)}">
                        <textarea id="section-content-${data.section_id}" class="form-control mb-2" rows="10">${escapeHtml(data.content)}</textarea>
                        <small class="text-muted d-block mb-2">Markdown suportado: títulos, listas, código, links, etc.</small>
                        <button class="btn btn-sm btn-primary" onclick="saveSection(${data.section_id})">Salvar</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSection(${data.section_id})">Excluir</button>
                    </div>
                </div>
            `;
            
            if (addButton) {
                sectionsContainer.insertBefore(createElementFromHTML(newSectionHtml), addButton);
            } else {
                sectionsContainer.insertAdjacentHTML('afterbegin', newSectionHtml);
            }
            
            initDragAndDrop();
            
            document.getElementById(`section-title-${data.section_id}`).focus();
        }
    });
}

function createElementFromHTML(htmlString) {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function editSection(sectionId) {
    document.getElementById(`section-display-${sectionId}`).classList.add('hidden');
    document.getElementById(`section-edit-${sectionId}`).classList.add('active');
    document.getElementById(`section-title-${sectionId}`).focus();
}

function saveSection(sectionId) {
    const title = document.getElementById(`section-title-${sectionId}`).value;
    const content = document.getElementById(`section-content-${sectionId}`).value;
    
    fetch(`/projects/section/${sectionId}/update/`, {
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
            document.getElementById(`section-title-display-${sectionId}`).innerHTML = `<h3 class="mb-0">${escapeHtml(title)}</h3>`;
            
            const contentDisplay = document.getElementById(`section-content-display-${sectionId}`);
            if (converter) {
                contentDisplay.innerHTML = converter.render(content);
            } else {
                contentDisplay.innerHTML = escapeHtml(content).replace(/\n/g, '<br>');
            }
            contentDisplay.setAttribute('data-markdown', content);
            
            document.getElementById(`section-display-${sectionId}`).classList.remove('hidden');
            document.getElementById(`section-edit-${sectionId}`).classList.remove('active');
        }
    });
}

function cancelEdit(sectionId) {
    location.reload();
}

function deleteSection(sectionId) {
    if (confirm('Tem certeza que deseja excluir esta seção?')) {
        fetch(`/projects/section/${sectionId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const sectionElement = document.getElementById(`section-${sectionId}`);
                if (sectionElement) {
                    sectionElement.remove();
                }
            }
        });
    }
}

function togglePinSection(sectionId) {
    fetch(`/projects/section/${sectionId}/pin/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function toggleLike(projectId) {
    fetch(`/projects/${projectId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        const likeButton = document.getElementById('likeButton');
        const likeIcon = likeButton.querySelector('i');
        const likesSpan = document.getElementById('likesCount');
        
        if (data.liked) {
            likeButton.classList.add('liked');
            likeIcon.className = 'fas fa-heart me-2';
        } else {
            likeButton.classList.remove('liked');
            likeIcon.className = 'far fa-heart me-2';
        }
        
        likesSpan.textContent = data.likes_count;
    });
}

function addComment(projectId) {
    const content = document.getElementById('commentContent').value;
    if (!content.trim()) {
        alert('Digite um comentário!');
        return;
    }
    
    fetch(`/projects/${projectId}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'content=' + encodeURIComponent(content)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function saveField(projectId, field) {
    let value;
    if (field === 'title') {
        value = document.getElementById('title-input').value;
    } else if (field === 'description') {
        value = document.getElementById('description-input').value;
    } else if (field === 'status') {
        value = document.getElementById('status-input').value;
    }
    
    fetch(`/projects/${projectId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'field=' + encodeURIComponent(field) + '&value=' + encodeURIComponent(value)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function editField(field) {
    document.getElementById(`${field}-display`).classList.add('hidden');
    document.getElementById(`${field}-edit`).classList.add('active');
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