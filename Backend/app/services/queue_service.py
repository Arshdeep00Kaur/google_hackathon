"""
Queue Service for Legal AI Assistant

This service integrates the RQ queue system with FastAPI,
providing an easy way to submit background jobs and track their progress.

Simple and beginner-friendly implementation.
"""

import uuid
import time
from typing import Dict, Any, Optional
from Queue.connection import get_chat_queue, get_document_queue, get_default_queue, check_queue_health
from Queue.worker import process_chat_query, process_document_upload, health_check_job
from app.models.job_tracking import JobTracker, JobType, JobStatus


class QueueService:
    """
    Queue Service for managing background jobs
    
    This service provides a simple interface for submitting jobs
    and tracking their progress using RQ and MongoDB.
    """
    
    def __init__(self):
        """Initialize the queue service"""
        self.job_tracker = JobTracker()
        print("🔧 Queue Service initialized")
    
    def submit_chat_query(self, query_text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a chat query for background processing
        
        Args:
            query_text (str): The user's query text
            user_id (str, optional): User identifier
            
        Returns:
            Dict: Job submission result with job_id
        """
        try:
            # Generate unique job ID
            job_id = f"chat_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            # Prepare job data
            job_data = {
                'query': query_text,
                'user_id': user_id,
                'submitted_at': time.time()
            }
            
            # Create job record in MongoDB
            self.job_tracker.create_job(job_id, JobType.CHAT_QUERY, job_data)
            
            # Submit job to queue
            chat_queue = get_chat_queue()
            if not chat_queue:
                raise Exception("Chat queue not available")
            
            # Enqueue the job
            rq_job = chat_queue.enqueue(
                process_chat_query,
                job_id,
                job_data,
                job_timeout='5m'  # 5 minute timeout
            )
            
            print(f"📤 Chat query submitted: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'submitted',
                'message': 'Chat query submitted for processing',
                'estimated_wait_time': '30-60 seconds'
            }
            
        except Exception as e:
            error_msg = f"Failed to submit chat query: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'status': 'failed'
            }
    
    def submit_document_upload(self, file_content: str, filename: str, 
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a document upload for background processing
        
        Args:
            file_content (str): Document content
            filename (str): Name of the uploaded file
            user_id (str, optional): User identifier
            
        Returns:
            Dict: Job submission result with job_id
        """
        try:
            # Generate unique job ID
            job_id = f"doc_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            # Prepare job data
            job_data = {
                'content': file_content,
                'filename': filename,
                'user_id': user_id,
                'submitted_at': time.time()
            }
            
            # Create job record in MongoDB
            self.job_tracker.create_job(job_id, JobType.DOCUMENT_UPLOAD, job_data)
            
            # Submit job to queue
            document_queue = get_document_queue()
            if not document_queue:
                raise Exception("Document queue not available")
            
            # Enqueue the job
            rq_job = document_queue.enqueue(
                process_document_upload,
                job_id,
                job_data,
                job_timeout='10m'  # 10 minute timeout for documents
            )
            
            print(f"📤 Document upload submitted: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'submitted',
                'message': f'Document "{filename}" submitted for processing',
                'estimated_wait_time': '1-3 minutes'
            }
            
        except Exception as e:
            error_msg = f"Failed to submit document upload: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'status': 'failed'
            }
    
    def submit_health_check(self) -> Dict[str, Any]:
        """
        Submit a health check job for testing the queue system
        
        Returns:
            Dict: Job submission result with job_id
        """
        try:
            # Generate unique job ID
            job_id = f"health_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            # Create job record in MongoDB
            job_data = {'test': 'health_check', 'submitted_at': time.time()}
            self.job_tracker.create_job(job_id, JobType.HEALTH_CHECK, job_data)
            
            # Submit job to default queue
            default_queue = get_default_queue()
            if not default_queue:
                raise Exception("Default queue not available")
            
            # Enqueue the job
            rq_job = default_queue.enqueue(
                health_check_job,
                job_id,
                job_timeout='30s'  # 30 second timeout
            )
            
            print(f"📤 Health check submitted: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'submitted',
                'message': 'Health check submitted',
                'estimated_wait_time': '5-10 seconds'
            }
            
        except Exception as e:
            error_msg = f"Failed to submit health check: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'status': 'failed'
            }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status and result of a job
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            Dict: Job status and result information
        """
        try:
            job = self.job_tracker.get_job(job_id)
            
            if not job:
                return {
                    'error': 'Job not found',
                    'job_id': job_id,
                    'status': 'not_found'
                }
            
            # Clean up the response
            response = {
                'job_id': job['job_id'],
                'job_type': job['job_type'],
                'status': job['status'],
                'created_at': job['created_at'],
                'updated_at': job['updated_at']
            }
            
            # Add result if available
            if job.get('result'):
                response['result'] = job['result']
            
            # Add error if failed
            if job.get('error'):
                response['error'] = job['error']
            
            # Add processing time if completed
            if job.get('processing_time'):
                response['processing_time_seconds'] = round(job['processing_time'], 2)
            
            return response
            
        except Exception as e:
            error_msg = f"Failed to get job status: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'job_id': job_id,
                'status': 'error'
            }
    
    def get_recent_jobs(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent jobs for monitoring
        
        Args:
            limit (int): Maximum number of jobs to return
            
        Returns:
            Dict: List of recent jobs
        """
        try:
            jobs = self.job_tracker.get_recent_jobs(limit)
            
            return {
                'jobs': jobs,
                'count': len(jobs),
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = f"Failed to get recent jobs: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'status': 'error'
            }
    
    def get_queue_health(self) -> Dict[str, Any]:
        """
        Get queue system health information
        
        Returns:
            Dict: Queue health status
        """
        try:
            # Check queue connections
            queue_status = check_queue_health()
            
            # Get job statistics
            job_stats = self.job_tracker.get_job_stats()
            
            # Combine information
            health_info = {
                'queue_system': queue_status,
                'job_statistics': job_stats,
                'mongodb_connected': self.job_tracker.mongo_conn.is_connected(),
                'overall_status': 'healthy' if queue_status.get('valkey_connected') else 'unhealthy',
                'timestamp': time.time()
            }
            
            return health_info
            
        except Exception as e:
            error_msg = f"Failed to get queue health: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'overall_status': 'error',
                'timestamp': time.time()
            }
    
    def cleanup_old_jobs(self, days: int = 7) -> Dict[str, Any]:
        """
        Clean up old completed jobs
        
        Args:
            days (int): Remove jobs older than this many days
            
        Returns:
            Dict: Cleanup result
        """
        try:
            deleted_count = self.job_tracker.cleanup_old_jobs(days)
            
            return {
                'deleted_jobs': deleted_count,
                'days_threshold': days,
                'status': 'success',
                'message': f'Cleaned up {deleted_count} old jobs'
            }
            
        except Exception as e:
            error_msg = f"Failed to cleanup jobs: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'status': 'error'
            }