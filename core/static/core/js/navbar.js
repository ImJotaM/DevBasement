document.addEventListener('DOMContentLoaded', function() {
    const searchModal = document.getElementById('globalSearchModal');
    const searchInput = document.getElementById('modalSearchInput');
    const bodyWrapper = document.getElementById('modalBodyWrapper');
    const suggestionsBox = document.getElementById('modalSuggestionsContainer');
    let debounceTimeout;

    if (!searchModal || !searchInput || !bodyWrapper || !suggestionsBox) return;

    searchModal.addEventListener('hidden.bs.modal', function () {
        searchInput.value = '';
        suggestionsBox.innerHTML = '';
        bodyWrapper.classList.add('d-none');
    });

    searchModal.addEventListener('shown.bs.modal', function () {
        searchInput.focus();
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const modalInstance = bootstrap.Modal.getOrCreateInstance(searchModal);
            modalInstance.show();
        }
    });

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            suggestionsBox.innerHTML = '';
            bodyWrapper.classList.add('d-none');
            return;
        }

        debounceTimeout = setTimeout(() => {
            fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    
                    if (data.suggestions && data.suggestions.length > 0) {
                        data.suggestions.forEach(item => {
                            const icon = item.type === 'project' ? 'fa-folder text-primary' : 'fa-user text-success';
                            
                            const link = document.createElement('a');
                            link.href = item.url;
                            link.className = 'list-group-item list-group-item-action d-flex align-items-center py-2.5 px-3 bg-white border-bottom';
                            link.innerHTML = `
                                <div class="me-3 text-center" style="width: 20px;">
                                    <i class="fas ${icon}" style="font-size: 0.95rem;"></i>
                                </div>
                                <div class="text-truncate flex-grow-1">
                                    <span class="d-block text-dark fw-medium small text-truncate mb-0">${item.title}</span>
                                    <small class="text-muted d-block text-truncate" style="font-size: 0.72rem; margin-top: -1px;">${item.subtitle}</small>
                                </div>
                                <div class="text-muted small ps-2" style="font-size: 0.7rem;">
                                    <i class="fas fa-arrow-right opacity-50"></i>
                                </div>
                            `;
                            suggestionsBox.appendChild(link);
                        });
                        bodyWrapper.classList.remove('d-none');
                    } else {
                        suggestionsBox.innerHTML = `
                            <div class="text-muted text-center py-4 px-3 small bg-white">
                                <i class="fas fa-search-minus d-block mb-2 fs-5 text-secondary"></i>
                                Nenhum resultado direto encontrado para "${query}". Pressione Enter para buscar detalhadamente.
                            </div>
                        `;
                        bodyWrapper.classList.remove('d-none');
                    }
                })
                .catch(err => console.error('Erro na requisição das sugestões:', err));
        }, 250);
    });
});