import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from src.domain.diagnostic_process import DiagnosticProcess
from src.domain.entities import Service, Circuit, Device
from src.domain.exceptions import ServiceNotFoundError, CircuitNotFoundError
from src.domain.value_objects import DiagnosticResult, RootCause

@pytest.mark.asyncio
class TestDiagnosticProcess:
    @pytest_asyncio.fixture
    async def diagnostic_process(self):
        """Create a diagnostic process with mocked dependencies."""
        # Mock dependencies
        inventory_service = AsyncMock()
        device_service = AsyncMock()
        notification_service = AsyncMock()
        diagnostic_repository = AsyncMock()
        
        dp = DiagnosticProcess(
            inventory_service=inventory_service,
            device_service=device_service,
            notification_service=notification_service,
            diagnostic_repository=diagnostic_repository
        )
        return dp
    
    async def test_initialize_diagnostic_process(self, diagnostic_process):
        # Arrange
        service_id = "TEST-SERVICE-001"
        
        # Act
        await diagnostic_process.initialize(service_id)
        
        # Assert
        diagnostic_process._diagnostic_repository.create_diagnostic.assert_called_once()
        
    async def test_validate_service_not_found(self, diagnostic_process):
        # Arrange
        service_id = "NONEXISTENT-SERVICE"
        diagnostic_process._inventory_service.get_service.return_value = None
        
        # Act & Assert
        with pytest.raises(ServiceNotFoundError):
            await diagnostic_process.validate_service(service_id)
            
    async def test_fetch_circuit_details(self, diagnostic_process):
        # Arrange
        service_id = "TEST-SERVICE-001"
        expected_circuit = Circuit(
            id="CKT-001",
            devices=[
                Device(id="DEV-001", ip="192.168.1.1", vendor="cisco"),
                Device(id="DEV-002", ip="192.168.1.2", vendor="huawei")
            ]
        )
        diagnostic_process._inventory_service.get_circuit.return_value = expected_circuit
        
        # Act
        circuit = await diagnostic_process.fetch_circuit(service_id)
        
        # Assert
        assert circuit == expected_circuit
        diagnostic_process._inventory_service.get_circuit.assert_called_once_with(service_id)
        
    async def test_process_circuit_devices(self, diagnostic_process):
        # Arrange
        devices = [
            Device(id="DEV-001", ip="192.168.1.1", vendor="cisco"),
            Device(id="DEV-002", ip="192.168.1.2", vendor="huawei")
        ]
        diagnostic_process._device_service.check_device.return_value = {"status": "OK"}
        
        # Act
        results = await diagnostic_process.process_circuit_devices(devices)
        
        # Assert
        assert len(results) == 2
        diagnostic_process._device_service.check_device.assert_called()
        
    async def test_analyze_results_fiber_cut(self, diagnostic_process):
        # Arrange
        device_results = [
            {"device_id": "DEV-001", "status": "DOWN", "interface_status": "LOS"},
            {"device_id": "DEV-002", "status": "DOWN", "interface_status": "LOS"}
        ]
        
        # Act
        root_cause = await diagnostic_process.analyze_results(device_results)
        
        # Assert
        assert root_cause == RootCause.FIBER_CUT
        
    async def test_save_conclusion(self, diagnostic_process):
        # Arrange
        diagnostic_id = "DIAG-001"
        root_cause = RootCause.FIBER_CUT
        summary = "Fiber cut detected between devices DEV-001 and DEV-002"
        
        # Act
        await diagnostic_process.save_conclusion(diagnostic_id, root_cause, summary)
        
        # Assert
        diagnostic_process._diagnostic_repository.update_diagnostic.assert_called_once()
