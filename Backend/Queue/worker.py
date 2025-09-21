"""
Background Worker for Legal AI Assistant

This module contains worker functions that process background jobs
using RQ (Redis Queue). Simple and beginner-friendly implementation.

Workers handle:
- Chat message processing
- Document analysis
- Long-running AI tasks
"""

import os
import sys
import time
import traceback
from typing import Dict, Any, Optional
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Queue.connection import get_chat_queue, get_document_queue, get_default_queue
    from app.services.query_service import QueryService
    from app.services.document_service import DocumentService
except ImportError as e:
    print(f"Warning: Could not import services: {e}")


class JobTracker:
    """
    Simple job tracking for MongoDB
    
    This class tracks job status and results in MongoDB
    """
    
    def __init__(self):
        """Initialize job tracker"""
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'legal_ai_jobs')
        self.collection_name = 'job_tracking'
        
        try:
            import pymongo
            self.client = pymongo.MongoClient(self.mongo_url)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"✅ Connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def update_job_status(self, job_id: str, status: str, result: Optional[Dict] = None):
        """
        Update job status in MongoDB
        
        Args:
            job_id (str): Job ID
            status (str): Job status ('pending', 'running', 'completed', 'failed')
            result (Dict, optional): Job result data
        """
        if not self.collection:
            print(f"⚠️ MongoDB not available, cannot track job {job_id}")
            return
        
        try:
            update_data = {
                'job_id': job_id,
                'status': status,
                'updated_at': time.time()
            }
            
            if result:
                update_data['result'] = result
            
            self.collection.update_one(
                {'job_id': job_id},
                {'$set': update_data},
                upsert=True
            )
            print(f"📝 Job {job_id} status updated to: {status}")
            
        except Exception as e:
            print(f"❌ Failed to update job {job_id}: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get job status from MongoDB
        
        Args:
            job_id (str): Job ID
            
        Returns:
            Dict: Job status and result or None if not found
        """
        if not self.collection:
            return None
        
        try:
            job = self.collection.find_one({'job_id': job_id})
            return job
        except Exception as e:
            print(f"❌ Failed to get job {job_id}: {e}")
            return None


# Global job tracker instance
job_tracker = JobTracker()


def process_chat_query(job_id: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a chat query in the background
    
    Args:
        job_id (str): Unique job identifier
        query_data (Dict): Query information containing 'query' text
        
    Returns:
        Dict: Processing result with answer and metadata
    """
    print(f"🔄 Starting chat query job: {job_id}")
    job_tracker.update_job_status(job_id, 'running')
    
    try:
        # Extract query text
        query_text = query_data.get('query', '')
        if not query_text:
            raise ValueError("No query text provided")
        
        print(f"🤖 Processing query: {query_text[:100]}...")
        
        # Use QueryService to process the query
        query_service = QueryService()
        result = query_service.process_query(query_text)
        
        # Prepare the response
        response = {
            'job_id': job_id,
            'query': query_text,
            'answer': result.get('answer', 'No answer generated'),
            'source_documents': result.get('source_documents', []),
            'processing_time': time.time(),
            'status': 'completed'
        }
        
        print(f"✅ Chat query completed: {job_id}")
        job_tracker.update_job_status(job_id, 'completed', response)
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to process chat query: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
        error_response = {
            'job_id': job_id,
            'error': error_msg,
            'status': 'failed',
            'processing_time': time.time()
        }
        
        job_tracker.update_job_status(job_id, 'failed', error_response)
        return error_response


def process_document_upload(job_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a document upload in the background
    
    Args:
        job_id (str): Unique job identifier
        document_data (Dict): Document information
        
    Returns:
        Dict: Processing result with document analysis
    """
    print(f"🔄 Starting document processing job: {job_id}")
    job_tracker.update_job_status(job_id, 'running')
    
    try:
        # Extract document information
        file_content = document_data.get('content', '')
        filename = document_data.get('filename', 'unknown.txt')
        
        if not file_content:
            raise ValueError("No document content provided")
        
        print(f"📄 Processing document: {filename}")
        
        # Use DocumentService to process the document
        document_service = DocumentService()
        result = document_service.process_document(file_content, filename)
        
        # Prepare the response
        response = {
            'job_id': job_id,
            'filename': filename,
            'category': result.get('category', 'unknown'),
            'processing_status': result.get('status', 'processed'),
            'document_id': result.get('document_id'),
            'processing_time': time.time(),
            'status': 'completed'
        }
        
        print(f"✅ Document processing completed: {job_id}")
        job_tracker.update_job_status(job_id, 'completed', response)
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to process document: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
        error_response = {
            'job_id': job_id,
            'error': error_msg,
            'status': 'failed',
            'processing_time': time.time()
        }
        
        job_tracker.update_job_status(job_id, 'failed', error_response)
        return error_response


def health_check_job(job_id: str) -> Dict[str, Any]:
    """
    Simple health check job for testing the queue system
    
    Args:
        job_id (str): Job identifier
        
    Returns:
        Dict: Health check result
    """
    print(f"🔄 Running health check job: {job_id}")
    job_tracker.update_job_status(job_id, 'running')
    
    try:
        # Simulate some work
        time.sleep(2)
        
        response = {
            'job_id': job_id,
            'status': 'completed',
            'message': 'Queue system is working properly!',
            'timestamp': time.time()
        }
        
        print(f"✅ Health check completed: {job_id}")
        job_tracker.update_job_status(job_id, 'completed', response)
        
        return response
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_response = {
            'job_id': job_id,
            'error': error_msg,
            'status': 'failed'
        }
        
        job_tracker.update_job_status(job_id, 'failed', error_response)
        return error_response


def run_worker():
    """
    Run the RQ worker to process background jobs
    
    This function starts the worker and listens for jobs on all queues.
    """
    try:
        from rq import Worker
        
        # Get all queues
        chat_queue = get_chat_queue()
        document_queue = get_document_queue()
        default_queue = get_default_queue()
        
        # Create list of queues to listen on
        queues = []
        if chat_queue:
            queues.append(chat_queue)
        if document_queue:
            queues.append(document_queue)
        if default_queue:
            queues.append(default_queue)
        
        if not queues:
            print("❌ No queues available. Check Valkey connection.")
            return
        
        print(f"🚀 Starting worker for queues: {[q.name for q in queues]}")
        
        # Create and start worker
        worker = Worker(queues)
        worker.work()
        
    except Exception as e:
        print(f"❌ Worker failed to start: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")


if __name__ == '__main__':
    """
    Start the worker when script is run directly
    
    Usage: python worker.py
    """
    print("🎯 Legal AI Assistant - Background Worker")
    print("=" * 50)
    run_worker()