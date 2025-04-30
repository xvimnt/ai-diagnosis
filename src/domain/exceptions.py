class DiagnosticError(Exception):
    """Base exception for diagnostic errors"""
    pass

class ServiceNotFoundError(DiagnosticError):
    """Raised when a service cannot be found"""
    pass

class CircuitNotFoundError(DiagnosticError):
    """Raised when a circuit cannot be found"""
    pass

class DeviceNotAccessibleError(DiagnosticError):
    """Raised when a device cannot be accessed via SNMP"""
    pass

class DiagnosticProcessError(DiagnosticError):
    """Raised when there's an error in the diagnostic process"""
    pass
