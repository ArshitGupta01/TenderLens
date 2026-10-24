"""
TenderLens - Production Backend Services
========================================
Exposes the multi-tier Web Intelligence, Document Intelligence,
and Storage / Cache infrastructure:
- TinyFishService (TinySearch, TinyFetch, Stealth TinyAgent)
- SerpAPIService (Google Public Search Fallback)
- DocumentProcessor (PyMuPDF coordinate and hyperlink parser)
- DoclingTableExtractor (Structured Table Extraction)
- RedisService (Atomic Cache and Task Broker)
- ObjectStorageService (S3 / MinIO Document Vault)
- SupabaseService (Postgres Database & Auth)
"""

from backend.services.tinyfish_service import TinyFishService, DiscoveredTender, FetchedDocument
from backend.services.serpapi_service import SerpAPIService, serpapi_service
from backend.services.document_processor import DocumentProcessor, ProcessedClauseChunk, ExtractedDocumentPackage
from backend.services.docling_service import DoclingTableExtractor, docling_extractor
from backend.services.redis_service import RedisService, redis_service
from backend.services.storage_service import ObjectStorageService, storage_service
from backend.services.supabase_service import SupabaseService
