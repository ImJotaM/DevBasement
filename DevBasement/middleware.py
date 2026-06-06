class NavigationHistoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.method == 'GET' 
            and not request.headers.get('x-requested-with') == 'XMLHttpRequest'
            and response.status_code == 200):
            
            current_path = request.get_full_path()
            
            if '/api/' in current_path or 'search-suggestions' in current_path:
                return response

            if 'nav_history' not in request.session:
                request.session['nav_history'] = []
            
            history = request.session['nav_history']
            
            if not history or history[-1] != current_path:
                history.append(current_path)
                
                if len(history) > 10:
                    history.pop(0)
                    
                request.session['nav_history'] = history

        return response