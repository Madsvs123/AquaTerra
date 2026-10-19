class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return response
        if not request.path.startswith("/api/") or request.path.startswith("/api/auth/"):
            return response
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response
        from audit.models import AuditLog

        resource = request.path.strip("/").split("/")
        AuditLog.objects.create(
            organization=getattr(request, "organization", None),
            actor=user,
            actor_email=getattr(user, "email", ""),
            action=request.method,
            path=request.path[:240],
            resource_type=resource[1] if len(resource) > 1 else "",
            status_code=getattr(response, "status_code", 0),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return response
