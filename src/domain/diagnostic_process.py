from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import logging

from .entities import Service, Circuit, Device
from .exceptions import ServiceNotFoundError, CircuitNotFoundError, DeviceNotAccessibleError
from .value_objects import DiagnosticResult, DeviceResult, RootCause

logger = logging.getLogger(__name__)

class DiagnosticProcess:
    def __init__(self, inventory_service, device_service, notification_service, diagnostic_repository):
        self._inventory_service = inventory_service
        self._device_service = device_service
        self._notification_service = notification_service
        self._diagnostic_repository = diagnostic_repository
        self._current_diagnostic_id = None
        
    async def initialize(self, service_id: str) -> str:
        """Initialize the diagnostic process for a service"""
        logger.info(f"Initializing diagnostic process for service {service_id}")
        self._current_diagnostic_id = await self._diagnostic_repository.create_diagnostic(
            service_id=service_id,
            start_time=datetime.now()
        )
        return self._current_diagnostic_id
        
    async def validate_service(self, service_id: str) -> Service:
        """Validate that the service exists"""
        service = await self._inventory_service.get_service(service_id)
        if not service:
            logger.error(f"Service {service_id} not found")
            raise ServiceNotFoundError(f"Service {service_id} not found")
        return service
        
    async def fetch_circuit(self, service_id: str) -> Circuit:
        """Fetch circuit details for the service"""
        circuit = await self._inventory_service.get_circuit(service_id)
        if not circuit:
            logger.error(f"Circuit not found for service {service_id}")
            raise CircuitNotFoundError(f"Circuit not found for service {service_id}")
        return circuit
        
    async def process_circuit_devices(self, devices: List[Device]) -> List[Dict[str, Any]]:
        """Process all devices in the circuit concurrently"""
        tasks = []
        for device in devices:
            tasks.append(self._process_single_device(device))
        return await asyncio.gather(*tasks)
        
    async def _process_single_device(self, device: Device) -> Dict[str, Any]:
        """Process a single device and return its diagnostic results"""
        try:
            return await self._device_service.check_device(device)
        except Exception as e:
            logger.error(f"Error processing device {device.id}: {str(e)}")
            return {
                "device_id": device.id,
                "status": "ERROR",
                "error": str(e)
            }
            
    async def analyze_results(self, device_results: List[Dict[str, Any]]) -> RootCause:
        """Analyze device results to determine root cause"""
        # Count devices with specific conditions
        los_count = sum(1 for r in device_results 
                       if r.get("status") == "DOWN" and r.get("interface_status") == "LOS")
        power_issues = sum(1 for r in device_results 
                          if r.get("status") == "DOWN" and r.get("power_status") == "OFF")
        
        if los_count >= 2:
            return RootCause.FIBER_CUT
        elif power_issues >= 1:
            return RootCause.POWER_ISSUE
        elif any(r.get("status") == "DOWN" for r in device_results):
            return RootCause.DEVICE_FAILURE
            
        return RootCause.OK
        
    async def save_conclusion(self, diagnostic_id: str, root_cause: RootCause, summary: str) -> None:
        """Save the diagnostic conclusion"""
        await self._diagnostic_repository.update_diagnostic(
            diagnostic_id=diagnostic_id,
            root_cause=root_cause,
            summary=summary,
            end_time=datetime.now()
        )
        
    async def send_notifications(self, diagnostic_result: DiagnosticResult) -> None:
        """Send notifications based on diagnostic results"""
        if diagnostic_result.root_cause in [RootCause.FIBER_CUT, RootCause.POWER_ISSUE]:
            await self._notification_service.send_urgent_notification(diagnostic_result)
            
    async def run(self, service_id: str) -> DiagnosticResult:
        """Run the complete diagnostic process"""
        try:
            # Initialize
            diagnostic_id = await self.initialize(service_id)
            
            # Validate service
            service = await self.validate_service(service_id)
            
            # Fetch circuit
            circuit = await self.fetch_circuit(service_id)
            
            # Process devices
            device_results = await self.process_circuit_devices(circuit.devices)
            
            # Analyze results
            root_cause = await self.analyze_results(device_results)
            
            # Create summary
            summary = self._create_summary(root_cause, device_results)
            
            # Save conclusion
            await self.save_conclusion(diagnostic_id, root_cause, summary)
            
            # Create diagnostic result
            diagnostic_result = DiagnosticResult(
                diagnostic_id=diagnostic_id,
                service_id=service_id,
                root_cause=root_cause,
                summary=summary,
                device_results=[
                    DeviceResult(
                        device_id=r["device_id"],
                        status=r["status"],
                        timestamp=datetime.now(),
                        details=r
                    ) for r in device_results
                ],
                start_time=datetime.now(),
                end_time=datetime.now(),
                status="COMPLETED"
            )
            
            # Send notifications if needed
            await self.send_notifications(diagnostic_result)
            
            return diagnostic_result
            
        except Exception as e:
            logger.error(f"Error in diagnostic process: {str(e)}")
            if diagnostic_id:
                await self._diagnostic_repository.update_diagnostic(
                    diagnostic_id=diagnostic_id,
                    status="ERROR",
                    error=str(e),
                    end_time=datetime.now()
                )
            raise
            
    def _create_summary(self, root_cause: RootCause, device_results: List[Dict[str, Any]]) -> str:
        """Create a human-readable summary of the diagnostic results"""
        affected_devices = [r["device_id"] for r in device_results if r.get("status") == "DOWN"]
        
        if root_cause == RootCause.FIBER_CUT:
            return f"Fiber cut detected affecting devices: {', '.join(affected_devices)}"
        elif root_cause == RootCause.POWER_ISSUE:
            return f"Power issue detected on devices: {', '.join(affected_devices)}"
        elif root_cause == RootCause.DEVICE_FAILURE:
            return f"Device failure detected on: {', '.join(affected_devices)}"
        elif root_cause == RootCause.OK:
            return "All devices operating normally"
        
        return "Unable to determine specific root cause"
