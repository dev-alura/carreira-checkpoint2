"""
Middleware para aceitar URLs da API com ou sem trailing slash.
Remove trailing slash de URLs que começam com /api/ antes do routing.
"""


class RemoveTrailingSlashMiddleware:
    """
    Remove trailing slash de URLs da API para permitir flexibilidade.
    URLs como /api/v1/clientes/ são convertidas para /api/v1/clientes
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Remove trailing slash apenas de URLs da API (não admin, auth, etc)
        if (
            request.path.startswith("/api/")
            and request.path.endswith("/")
            and request.path != "/api/"
        ):
            # Remove a barra final
            request.path_info = request.path_info.rstrip("/")
            request.path = request.path.rstrip("/")

        response = self.get_response(request)
        return response
