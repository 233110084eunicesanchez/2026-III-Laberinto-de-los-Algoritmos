from .access import is_manager
def navigation(request):
    return {'manager':is_manager(request.user)}
