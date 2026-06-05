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

document.querySelectorAll('.project-card .like-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        const csrftoken = getCookie('csrftoken');
        const projectId = this.getAttribute('data-project-id');

        if (!url) return;
        if (!csrftoken) {
            window.location.href = '/accounts/login/';
            return;
        }

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 403 || response.status === 401) {
                window.location.href = '/accounts/login/';
                return;
            }
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Erro na requisição'); });
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                document.querySelectorAll(`.like-btn[data-project-id="${projectId}"]`).forEach(btn => {
                    const icon = btn.querySelector('i');
                    const countSpan = btn.querySelector('.likes-count');

                    if (data.liked) {
                        btn.classList.add('text-danger');
                        if (icon) icon.className = 'fas fa-heart text-danger';
                    } else {
                        btn.classList.remove('text-danger');
                        if (icon) icon.className = 'far fa-heart';
                    }
                    
                    if (countSpan && data.likes_count !== undefined) {
                        countSpan.textContent = data.likes_count;
                    }
                });
            }
        })
        .catch(err => {
            console.error('Erro ao curtir o projeto:', err);
        });
    });
});

document.querySelectorAll('.project-card .favorite-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        const csrftoken = getCookie('csrftoken');
        const projectId = this.getAttribute('data-project-id');

        if (!url) return;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 402 || response.redirected || response.url.includes('login')) {
                window.location.href = "/accounts/login/"; 
                return;
            }
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Erro na requisição'); });
            }
            return response.json();
        })
        .then(data => {
            if (data && data.favorited !== undefined) {
                document.querySelectorAll(`.favorite-btn[data-project-id="${projectId}"]`).forEach(btn => {
                    const icon = btn.querySelector('i');
                    
                    if (data.favorited) {
                        btn.classList.remove('text-muted');
                        btn.classList.add('text-warning');
                        if (icon) icon.className = 'fas fa-star';
                    } else {
                        btn.classList.remove('text-warning');
                        btn.classList.add('text-muted');
                        if (icon) icon.className = 'far fa-star';
                    }
                });
            }
        })
        .catch(err => {
            console.error("Erro ao processar o favorito:", err);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const reportModalEl = document.getElementById('reportModal');
    if (!reportModalEl) return;
    
    const reportModal = new bootstrap.Modal(reportModalEl);
    const reportButtons = document.querySelectorAll('.btn-report');
    const modalProjectId = document.getElementById('modalProjectId');
    const modalProjectTitle = document.getElementById('modalProjectTitle');
    const reportForm = document.getElementById('reportForm');
    const modalErrorMessage = document.getElementById('modalErrorMessage');
    const btnAdminDelete = document.getElementById('btnAdminDelete');

    let activeProjectUsername = '';
    let activeProjectSlug = '';

    reportButtons.forEach(button => {
        button.addEventListener('click', function () {
            const projectId = this.getAttribute('data-project-id');
            const projectTitle = this.getAttribute('data-project-title');
            
            activeProjectUsername = this.getAttribute('data-project-username');
            activeProjectSlug = this.getAttribute('data-project-slug');
            
            reportForm.reset();
            modalErrorMessage.classList.add('d-none');
            modalErrorMessage.textContent = '';
            
            modalProjectId.value = projectId;
            modalProjectTitle.textContent = projectTitle;
            
            reportModal.show();
        });
    });

    if (reportForm) {
        reportForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(reportForm);
            formData.append('action', 'report');
            sendReportForModeration(activeProjectUsername, activeProjectSlug, formData);
        });
    }

    if (btnAdminDelete) {
        btnAdminDelete.addEventListener('click', function () {
            if (confirm("Tem certeza absoluta de que deseja excluir permanentemente este projeto da plataforma?")) {
                const csrfToken = reportForm.querySelector('[name=csrfmiddlewaretoken]').value;
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);
                formData.append('action', 'delete');
                sendReportForModeration(activeProjectUsername, activeProjectSlug, formData);
            }
        });
    }

    function sendReportForModeration(username, slug, formData) {
        modalErrorMessage.classList.add('d-none');
        
        fetch(`/${username}/${slug}/report/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(res => {
            if (res.status === 200) {
                alert(res.body.message);
                reportModal.hide();
                if (res.body.status === 'deleted') {
                    window.location.reload();
                }
            } else {
                modalErrorMessage.textContent = res.body.error || 'Ocorreu um erro inesperado.';
                modalErrorMessage.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            modalErrorMessage.textContent = 'Erro ao processar a requisição no servidor.';
            modalErrorMessage.classList.remove('d-none');
        });
    }
});