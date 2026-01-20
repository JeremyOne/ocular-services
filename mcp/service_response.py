"""
Service Response Data Class
A reusable class for representing structured responses from security scanning services.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class ServiceResponse:
    """
    Represents a standardized response from a security scanning service.
    
    Attributes:
        service: Name of the service that generated the response (e.g., 'ping', 'nmap')
        process_time_ms: Processing time in milliseconds
        target: The target IP, domain, or resource that was scanned
        arguments: Dictionary of arguments passed to the service
        return_code: Exit code from the service execution (0 = success)
        raw_output: Raw stdout from the service
        raw_error: Raw stderr from the service
    """
    service: str
    process_start_time: datetime = field(default_factory=datetime.utcnow)
    process_time_ms: int
    process_end_time: datetime
    target: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    raw_command: str = ""
    return_code: int = 0
    raw_output: str = ""
    raw_error: str = ""
    #structured_output: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ServiceResponse to a dictionary.
        
        Returns:
            Dictionary representation of the response
        """
        return {
            "service": self.service,
            "process_start_time": self.process_start_time,
            "target": self.target,
            "arguments": self.arguments,
            "return_code": self.return_code,
            "raw_command": self.raw_command,
            "raw_output": self.raw_output,
            "raw_error": self.raw_error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceResponse':
        """
        Create a ServiceResponse from a dictionary.
        
        Args:
            data: Dictionary containing response data
            
        Returns:
            ServiceResponse instance
        """
        return cls(
            service=data.get("service", ""),
            process_start_time=data.get("process_start_time", datetime.utcnow()),
            process_time_ms=data.get("process_time_ms", 0),
            process_end_time=data.get("process_end_time", datetime.utcnow()),
            target=data.get("target", ""),
            arguments=data.get("arguments", {}),
            return_code=data.get("return_code", 0),
            raw_command=data.get("raw_command", ""),
            raw_error=data.get("raw_error", ""),
            structured_output=data.get("structured_output", {})
        )
    
    def is_successful(self) -> bool:
        """
        Check if the service execution was successful.
        
        Returns:
            True if return_code is 0, False otherwise
        """
        return self.return_code == 0
    
    def has_errors(self) -> bool:
        """
        Check if there were any errors during execution.
        
        Returns:
            True if raw_error contains data or return_code is non-zero
        """
        return bool(self.raw_error) or self.return_code != 0

    def end_process_timer(self):
        """
        Set the process end time to current time and calculate process_time_ms.
        """
        self.process_end_time = datetime.utcnow()
        self.process_time_ms = int((self.process_end_time - self.process_start_time).total_seconds() * 1000)

    def add_error(self, error_message: str, return_code: Optional[int] = None):
        """
        Append an error message to the raw_error field.
        
        Args:
            error_message: The error message to append
            return_code: Optional return code to set
        """
        if return_code is not None:
            self.return_code = return_code
        if self.raw_error:
            self.raw_error += "\n"
        self.raw_error += error_message

        self.end_process_timer()
    
    def __repr__(self) -> str:
        """String representation of the ServiceResponse."""
        return (f"ServiceResponse(service='{self.service}', "
                f"target='{self.target}', "
                f"process_time_ms={self.process_time_ms}, "
                f"return_code={self.return_code})")
