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
            alert('Não foi possível processar a ação.');
        });
    });
});