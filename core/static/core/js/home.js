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

document.querySelectorAll('.follow-btn').forEach(button => {
    button.addEventListener('click', function() {
        const username = this.getAttribute('data-username');
        const csrftoken = getCookie('csrftoken');
        
        const url = `/accounts/follow/${username}/`; 
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro na requisição. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.is_following) {
                this.textContent = 'Seguindo';
                this.className = 'btn btn-outline-primary btn-sm rounded-pill px-3 follow-btn';
            } else {
                this.textContent = 'Seguir';
                this.className = 'btn btn-primary btn-sm rounded-pill px-3 follow-btn';
            }
        })
        .catch(error => {
            console.error('Erro detalhado:', error);
            alert('Não foi possível processar a ação. Veja o console do desenvolvedor para mais detalhes.');
        });
    });
});

document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function() {
        const csrftoken = getCookie('csrftoken');
        const icon = this.querySelector('i');
        const countSpan = this.querySelector('.likes-count');

        if (!csrftoken) {
            window.location.href = '/accounts/login/';
            return;
        }

        const url = this.getAttribute('data-url');

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
                throw new Error(`Erro na requisição. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                countSpan.textContent = data.likes_count;

                if (data.liked) {
                    this.classList.add('text-danger');
                    icon.className = 'fas fa-heart text-danger';
                } else {
                    this.classList.remove('text-danger');
                    icon.className = 'far fa-heart';
                }
            }
        })
        .catch(error => {
            console.error('Erro ao curtir o projeto:', error);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const favoriteButtons = document.querySelectorAll(".favorite-btn");

    favoriteButtons.forEach(button => {
        button.addEventListener("click", function () {
            const projectId = this.getAttribute("data-project-id");
            const url = this.getAttribute("data-url");
            const icon = this.querySelector("i");
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            if (!csrfToken) {
                console.error("CSRF Token não encontrado na página.");
                return;
            }

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                if (response.status === 402 || response.redirected || response.url.includes('login')) {
                    window.location.href = "/accounts/login/"; 
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.favorited !== undefined) {
                    if (data.favorited) {
                        icon.classList.remove("far");
                        icon.classList.add("fas");
                        this.classList.remove("text-muted");
                        this.classList.add("text-warning");
                    } else {
                        icon.classList.remove("fas");
                        icon.classList.add("far");
                        this.classList.remove("text-warning");
                        this.classList.add("text-muted");
                    }
                }
            })
            .catch(error => {
                console.error("Erro ao processar o favorito:", error);
            });
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

    reportForm.addEventListener('submit', function (e) {
        e.preventDefault();
        
        const formData = new FormData(reportForm);
        formData.append('action', 'report');

        sendReportForModeration(activeProjectUsername, activeProjectSlug, formData);
    });

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