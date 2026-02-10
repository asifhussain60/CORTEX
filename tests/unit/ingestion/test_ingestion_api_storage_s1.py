"""
Phase 49 S1: Ingestion API & Storage - Document Upload & Validation

Tests for document ingestion endpoint, validation, and storage.

Authority: phase-49-document-ingestion-pipeline.yaml
Acceptance Criteria:
  - AC-PHASE49-S1-001: Upload accepts Word/Excel/PPT/PDF/Markdown
  - AC-PHASE49-S1-002: MIME type validation prevents malicious uploads
  - AC-PHASE49-S1-003: Documents stored with encryption at rest
"""

import pytest
import tempfile
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class DocumentMetadata:
    """Document metadata record."""
    doc_id: str
    filename: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime
    uploaded_by: str
    storage_path: str
    checksum: str
    encrypted: bool = True
    status: str = "pending_extraction"


ALLOWED_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-word.document.macroEnabled.12": ".docm",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel.sheet.macroEnabled.12": ".xlsm",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12": ".pptm",
    "application/pdf": ".pdf",
    "text/markdown": ".md",
    "text/plain": ".txt",
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


class DocumentStorage:
    """Abstract document storage adapter."""
    
    def store(self, filename: str, content: bytes, encrypted: bool = True) -> str:
        """Store document and return storage path."""
        raise NotImplementedError
    
    def retrieve(self, storage_path: str) -> bytes:
        """Retrieve document from storage."""
        raise NotImplementedError
    
    def delete(self, storage_path: str) -> bool:
        """Delete document from storage."""
        raise NotImplementedError


class LocalFilesystemStorage(DocumentStorage):
    """Local filesystem storage adapter."""
    
    def __init__(self, base_path: str):
        """Initialize with base storage path."""
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def store(self, filename: str, content: bytes, encrypted: bool = True) -> str:
        """Store document locally."""
        # Simple encryption stub: XOR with fixed key (real implementation would use proper encryption)
        if encrypted:
            content = bytes([b ^ 0xAA for b in content])
        
        storage_path = os.path.join(self.base_path, filename)
        with open(storage_path, 'wb') as f:
            f.write(content)
        
        return storage_path
    
    def retrieve(self, storage_path: str) -> bytes:
        """Retrieve document from local storage."""
        with open(storage_path, 'rb') as f:
            content = f.read()
        
        # Decrypt stub
        content = bytes([b ^ 0xAA for b in content])
        return content
    
    def delete(self, storage_path: str) -> bool:
        """Delete document from local storage."""
        if os.path.exists(storage_path):
            os.remove(storage_path)
            return True
        return False


class DocumentIngestionOrchestrator:
    """Document ingestion orchestrator."""
    
    def __init__(self, storage: DocumentStorage):
        """Initialize with storage adapter."""
        self.storage = storage
        self.documents: Dict[str, DocumentMetadata] = {}
        self.upload_count = 0
    
    def validate_mime_type(self, mime_type: str) -> bool:
        """Validate MIME type is allowed."""
        return mime_type in ALLOWED_MIMES
    
    def validate_file_size(self, size_bytes: int) -> bool:
        """Validate file size is within limits."""
        return 0 < size_bytes <= MAX_FILE_SIZE
    
    def calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA256 checksum of content."""
        return hashlib.sha256(content).hexdigest()
    
    def upload_document(self, filename: str, content: bytes, mime_type: str,
                       uploaded_by: str) -> Optional[DocumentMetadata]:
        """
        Upload document with validation.
        
        Args:
            filename: Original filename
            content: File content bytes
            mime_type: MIME type
            uploaded_by: User uploading document
        
        Returns:
            DocumentMetadata if successful, None if validation failed
        """
        # Validate MIME type
        if not self.validate_mime_type(mime_type):
            return None
        
        # Validate file size
        if not self.validate_file_size(len(content)):
            return None
        
        # Store document
        storage_path = self.storage.store(filename, content, encrypted=True)
        
        # Create metadata record
        metadata = DocumentMetadata(
            doc_id=f"doc_{self.upload_count}",
            filename=filename,
            mime_type=mime_type,
            size_bytes=len(content),
            uploaded_at=datetime.now(),
            uploaded_by=uploaded_by,
            storage_path=storage_path,
            checksum=self.calculate_checksum(content),
            encrypted=True,
            status="pending_extraction"
        )
        
        self.documents[metadata.doc_id] = metadata
        self.upload_count += 1
        
        return metadata
    
    def get_document_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID."""
        return self.documents.get(doc_id)
    
    def list_documents(self) -> List[DocumentMetadata]:
        """List all documents."""
        return list(self.documents.values())
    
    def get_document_by_status(self, status: str) -> List[DocumentMetadata]:
        """Get documents by status."""
        return [doc for doc in self.documents.values() if doc.status == status]


# ============================================================================
# TESTS: Ingestion API Upload Validation (AC-PHASE49-S1-001)
# ============================================================================

class TestDocumentUploadValidation:
    """Test document upload and MIME type validation."""
    
    def test_upload_word_document(self):
        """Test uploading Word document (.docx)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Mock Word document content"
            metadata = orchestrator.upload_document(
                filename="policy.docx",
                content=content,
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                uploaded_by="user1"
            )
            
            assert metadata is not None
            assert metadata.filename == "policy.docx"
            assert metadata.status == "pending_extraction"
    
    def test_upload_excel_document(self):
        """Test uploading Excel document (.xlsx)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Mock Excel content"
            metadata = orchestrator.upload_document(
                filename="standards.xlsx",
                content=content,
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                uploaded_by="user1"
            )
            
            assert metadata is not None
            assert metadata.filename == "standards.xlsx"
    
    def test_upload_pdf_document(self):
        """Test uploading PDF document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Mock PDF content"
            metadata = orchestrator.upload_document(
                filename="compliance.pdf",
                content=content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            assert metadata is not None
            assert metadata.mime_type == "application/pdf"
    
    def test_upload_markdown_document(self):
        """Test uploading Markdown document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"# Architecture Document\n\n## Overview\n\nArchitecture details."
            metadata = orchestrator.upload_document(
                filename="architecture.md",
                content=content,
                mime_type="text/markdown",
                uploaded_by="user1"
            )
            
            assert metadata is not None
            assert metadata.mime_type == "text/markdown"
    
    def test_upload_powerpoint_document(self):
        """Test uploading PowerPoint document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Mock PowerPoint content"
            metadata = orchestrator.upload_document(
                filename="training.pptx",
                content=content,
                mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                uploaded_by="user1"
            )
            
            assert metadata is not None


# ============================================================================
# TESTS: MIME Type Validation (AC-PHASE49-S1-002)
# ============================================================================

class TestMIMETypeValidation:
    """Test MIME type validation prevents malicious uploads."""
    
    def test_reject_executable_mime_type(self):
        """Test rejection of executable MIME types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Malicious executable"
            metadata = orchestrator.upload_document(
                filename="malware.exe",
                content=content,
                mime_type="application/x-msdownload",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
    def test_reject_script_mime_type(self):
        """Test rejection of script MIME types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            metadata = orchestrator.upload_document(
                filename="payload.js",
                content=b"alert('xss')",
                mime_type="application/javascript",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
    def test_reject_html_mime_type(self):
        """Test rejection of HTML MIME type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            metadata = orchestrator.upload_document(
                filename="payload.html",
                content=b"<script>alert('xss')</script>",
                mime_type="text/html",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
    def test_reject_zip_mime_type(self):
        """Test rejection of ZIP MIME type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            metadata = orchestrator.upload_document(
                filename="archive.zip",
                content=b"PK\x03\x04",
                mime_type="application/zip",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
# ============================================================================
# TESTS: File Size Validation
# ============================================================================

class TestFileSizeValidation:
    """Test file size validation."""
    
    def test_reject_empty_file(self):
        """Test rejection of empty files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            metadata = orchestrator.upload_document(
                filename="empty.pdf",
                content=b"",
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
    def test_reject_oversized_file(self):
        """Test rejection of files exceeding 100 MB limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            # Create content exceeding 100 MB
            oversized_content = b"x" * (MAX_FILE_SIZE + 1)
            
            metadata = orchestrator.upload_document(
                filename="huge.pdf",
                content=oversized_content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            assert metadata is None
    
    def test_accept_max_size_boundary(self):
        """Test acceptance at 100 MB boundary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            # Create content exactly at limit
            max_content = b"x" * MAX_FILE_SIZE
            
            metadata = orchestrator.upload_document(
                filename="maxsize.pdf",
                content=max_content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            assert metadata is not None


# ============================================================================
# TESTS: Storage & Encryption (AC-PHASE49-S1-003)
# ============================================================================

class TestDocumentStorage:
    """Test document storage with encryption."""
    
    def test_document_stored_with_encryption(self):
        """Test documents are stored encrypted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Sensitive compliance data"
            metadata = orchestrator.upload_document(
                filename="secret.pdf",
                content=content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            assert metadata is not None
            assert metadata.encrypted is True
            
            # Verify encryption: raw file content should not match original
            with open(metadata.storage_path, 'rb') as f:
                stored_content = f.read()
            
            assert stored_content != content
    
    def test_document_retrieval_decrypts(self):
        """Test document retrieval decrypts content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Confidential information"
            metadata = orchestrator.upload_document(
                filename="confidential.pdf",
                content=content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            # Retrieve and verify decryption
            retrieved = storage.retrieve(metadata.storage_path)
            assert retrieved == content
    
    def test_checksum_stored_with_metadata(self):
        """Test checksum is calculated and stored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Document content for checksum"
            metadata = orchestrator.upload_document(
                filename="test.pdf",
                content=content,
                mime_type="application/pdf",
                uploaded_by="user1"
            )
            
            expected_checksum = hashlib.sha256(content).hexdigest()
            assert metadata.checksum == expected_checksum


# ============================================================================
# TESTS: Document Metadata & Tracking
# ============================================================================

class TestDocumentMetadata:
    """Test document metadata tracking."""
    
    def test_document_metadata_recorded(self):
        """Test all metadata is recorded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            content = b"Test content"
            metadata = orchestrator.upload_document(
                filename="audit.pdf",
                content=content,
                mime_type="application/pdf",
                uploaded_by="compliance_team"
            )
            
            assert metadata.filename == "audit.pdf"
            assert metadata.mime_type == "application/pdf"
            assert metadata.uploaded_by == "compliance_team"
            assert metadata.size_bytes == len(content)
            assert metadata.uploaded_at is not None
            assert metadata.status == "pending_extraction"
    
    def test_list_all_documents(self):
        """Test listing all uploaded documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            # Upload multiple documents
            orchestrator.upload_document("doc1.pdf", b"content1", "application/pdf", "user1")
            orchestrator.upload_document("doc2.docx", b"content2", 
                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                        "user2")
            orchestrator.upload_document("doc3.md", b"content3", "text/markdown", "user3")
            
            documents = orchestrator.list_documents()
            assert len(documents) == 3
    
    def test_get_documents_by_status(self):
        """Test filtering documents by status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            # Upload documents
            metadata1 = orchestrator.upload_document("doc1.pdf", b"c1", "application/pdf", "user1")
            metadata2 = orchestrator.upload_document("doc2.pdf", b"c2", "application/pdf", "user2")
            
            # Change status
            metadata1.status = "extracted"
            orchestrator.documents[metadata1.doc_id] = metadata1
            
            # Query by status
            pending = orchestrator.get_document_by_status("pending_extraction")
            extracted = orchestrator.get_document_by_status("extracted")
            
            assert len(pending) == 1
            assert len(extracted) == 1


# ============================================================================
# TESTS: Multi-Format Support
# ============================================================================

class TestMultiFormatSupport:
    """Test support for multiple document formats."""
    
    def test_all_allowed_formats_supported(self):
        """Test all allowed formats can be uploaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFilesystemStorage(tmpdir)
            orchestrator = DocumentIngestionOrchestrator(storage)
            
            formats = [
                ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                ("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
                ("document.pdf", "application/pdf"),
                ("readme.md", "text/markdown"),
            ]
            
            for filename, mime_type in formats:
                metadata = orchestrator.upload_document(
                    filename=filename,
                    content=b"Content for " + filename.encode(),
                    mime_type=mime_type,
                    uploaded_by="user1"
                )
                
                assert metadata is not None
                assert metadata.filename == filename
    
    def test_mime_types_mapped_to_extensions(self):
        """Test MIME types are mapped to file extensions."""
        # Verify all ALLOWED_MIMES entries have correct mapping
        assert len(ALLOWED_MIMES) == 9
        
        for mime_type, extension in ALLOWED_MIMES.items():
            assert extension.startswith(".")
            assert len(extension) > 1
