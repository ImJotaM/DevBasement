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
        const followersCounter = document.getElementById('followers-count-val');
        
        if (!username) return;
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
                return response.json().then(err => { throw new Error(err.error || 'Erro na requisição'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.is_following) {
                this.textContent = 'Seguindo';
                this.className = 'btn btn-outline-primary btn-sm rounded-pill px-3 follow-btn';
            } else {
                this.innerHTML = '<i class="fas fa-user-plus me-1"></i> Seguir';
                this.className = 'btn btn-primary btn-sm rounded-pill px-3 follow-btn';
            }
            
            if (followersCounter && data.followers_count !== undefined) {
                followersCounter.textContent = data.followers_count;
            }
        })
        .catch(err => {
            alert(err.message || 'Houve um erro ao processar a ação.');
        });
    });
});

document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        const csrftoken = getCookie('csrftoken');
        const projectId = this.getAttribute('data-project-id');

        if (!url) return;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Erro na requisição'); });
            }
            return response.json();
        })
        .then(data => {
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
        })
        .catch(err => {
            alert(err.message || 'Houve um erro ao processar a ação.');
        });
    });
});

document.querySelectorAll('.favorite-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        const csrftoken = getCookie('csrftoken');
        const projectId = this.getAttribute('data-project-id');

        if (!url) return;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
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
                        if (icon) {
                            icon.className = 'fas fa-star';
                        }
                    } else {
                        btn.classList.remove('text-warning');
                        btn.classList.add('text-muted');
                        if (icon) {
                            icon.className = 'far fa-star';
                        }
                    }
                });
            }
        })
        .catch(err => {
            alert(err.message || 'Houve um erro ao processar a ação.');
        });
    });
});