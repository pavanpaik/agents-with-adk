"""
Data models for code review findings.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any

class Severity(Enum):
    """Severity levels for findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FindingType(Enum):
    """Categories of findings."""
    SECURITY = "SECURITY"
    ARCHITECTURE = "ARCHITECTURE"
    PERFORMANCE = "PERFORMANCE"
    QUALITY = "QUALITY"
    PYTHONIC = "PYTHONIC"
    TYPING = "TYPING"
    TESTING = "TESTING"
    DOCUMENTATION = "DOCUMENTATION"

@dataclass
class CodeLocation:
    """Represents a location in code."""
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    column_start: Optional[int] = None
    column_end: Optional[int] = None

    def __str__(self) -> str:
        if self.line_end and self.line_end != self.line_start:
            return f"{self.file_path}:{self.line_start}-{self.line_end}"
        return f"{self.file_path}:{self.line_start}"

@dataclass
class Finding:
    """Represents a single code review finding."""
    type: FindingType
    severity: Severity
    title: str
    description: str
    location: CodeLocation
    code_snippet: str
    impact: str
    remediation: str
    fixed_code: Optional[str] = None
    references: List[str] = None
    cvss_score: Optional[float] = None
    confidence: float = 1.0  # 0.0 to 1.0
    pep_references: List[str] = None  # PEP standards related to this finding

    def __post_init__(self):
        if self.references is None:
            self.references = []
        if self.pep_references is None:
            self.pep_references = []

@dataclass
class ReviewResult:
    """Results from a single reviewer agent."""
    reviewer: str
    findings: List[Finding]
    execution_time: float
    files_reviewed: int
    summary: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AggregatedReview:
    """Final aggregated review from all reviewers."""
    overall_score: float  # 0-100
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings_by_severity: Dict[Severity, List[Finding]]
    findings_by_type: Dict[FindingType, List[Finding]]
    findings_by_file: Dict[str, List[Finding]]
    top_issues: List[Finding]
    quick_wins: List[Finding]
    executive_summary: str
    detailed_report: str
