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
        const projectId = this.getAttribute('data-project-id');
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