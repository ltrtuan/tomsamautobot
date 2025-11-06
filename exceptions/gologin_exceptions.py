# exceptions/gologin_exceptions.py

class ProxyAssignmentFailed(Exception):
    """
    Custom exception raised when proxy assignment fails for a profile.
    Used to stop entire action when proxy is REQUIRED (e.g., YouTube views to avoid IP duplication).
    """
    pass
