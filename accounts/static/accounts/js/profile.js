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

document.querySelectorAll('.profile-page-follow-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        const csrftoken = getCookie('csrftoken');
        const followersCounter = document.getElementById('followers-count-val');

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
                this.className = 'btn-follow following profile-page-follow-btn';
            } else {
                this.innerHTML = '<i class="fas fa-user-plus me-1"></i> Seguir';
                this.className = 'btn-follow profile-page-follow-btn';
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
        const icon = this.querySelector('i');
        const countSpan = this.querySelector('span');

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
            if (data.liked) {
                this.classList.add('text-danger');
                icon.className = 'fas fa-heart';
            } else {
                this.classList.remove('text-danger');
                icon.className = 'far fa-heart';
            }
            
            if (countSpan && data.likes_count !== undefined) {
                countSpan.textContent = data.likes_count;
            }
        })
        .catch(err => {
            alert(err.message || 'Houve um erro ao processar a ação.');
        });
    });
});