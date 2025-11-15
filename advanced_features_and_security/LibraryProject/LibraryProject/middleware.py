"""
Custom Security Middleware for enhanced HTTP security headers
"""

class SecurityHeadersMiddleware:
    """
    Comprehensive security headers middleware for enhanced protection
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Comprehensive security headers
        security_headers = {
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Control referrer information
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Feature policy - restrict browser features
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=()',
            
            # Content Security Policy
            'Content-Security-Policy': self.build_csp_header(),
        }
        
        # Add all security headers to response
        for header, value in security_headers.items():
            if value and header not in response:
                response[header] = value
        
        return response

    def build_csp_header(self):
        """
        Build Content Security Policy header from settings
        """
        from django.conf import settings
        
        directives = getattr(settings, 'CSP_DIRECTIVES', {})
        
        # Default restrictive CSP
        default_directives = {
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'script-src': ["'self'"],
            'img-src': ["'self'", "data:", "https:"],
            'font-src': ["'self'"],
            'connect-src': ["'self'"],
            'frame-ancestors': ["'none'"],
            'base-uri': ["'self'"],
            'form-action': ["'self'"],
        }
        
        # Merge with settings
        for key, value in directives.items():
            default_directives[key] = value
        
        # Build CSP header string
        csp_parts = []
        for directive, sources in default_directives.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
        
        return '; '.join(csp_parts)


class SSLMiddleware:
    """
    Additional SSL/TLS security middleware
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request is secure
        if not request.is_secure() and not self.is_development():
            # Log insecure access attempts
            import logging
            logger = logging.getLogger('bookshelf.security')
            logger.warning(f"Insecure access attempt from {request.META.get('REMOTE_ADDR')}")
        
        response = self.get_response(request)
        return response

    def is_development(self):
        from django.conf import settings
        return settings.DEBUG
