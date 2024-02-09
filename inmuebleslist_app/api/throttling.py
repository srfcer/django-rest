from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class ComentarioCreateThrottle(UserRateThrottle):
    scope = "comentario-create"
    
class ComentarioListThrottle(UserRateThrottle):
    scope = "comentario-list"