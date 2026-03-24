from rest_framework import permissions

class EsAdminONoBorrar(permissions.BasePermission):
    """
    Regla de permisos personalizada:
    - Usuarios no autenticados: No pueden hacer nada.
    - Médicos (Usuarios normales): Pueden VER, CREAR y EDITAR (GET, POST, PUT, PATCH).
    - Admin (Superusuario): Puede hacer todo, incluyendo BORRAR (DELETE).
    """

    def has_permission(self, request, view):
        # 1. ¿Está logueado? Si no, puerta cerrada.
        if not request.user.is_authenticated:
            return False

        # 2. Si intenta BORRAR (DELETE), ¿Es el Admin supremo?
        if request.method == 'DELETE':
            return request.user.is_superuser

        # 3. Para todo lo demás (Crear, Ver, Editar), pase adelante señor Médico.
        return True