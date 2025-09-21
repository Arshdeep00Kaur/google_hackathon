"""
MongoDB Models for Job Tracking

Simple MongoDB schemas for tracking background jobs
in the Legal AI Assistant system.
"""

import os
import time
from typing import Dict, Any, Optional, List
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    """Job type enumeration"""
    CHAT_QUERY = "chat_query"
    DOCUMENT_UPLOAD = "document_upload"
    HEALTH_CHECK = "health_check"


class MongoDBConnection:
    """
    Simple MongoDB connection manager
    
    Handles connection to MongoDB for job tracking
    """
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'legal_ai_jobs')
        
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            import pymongo
            
            self.client = pymongo.MongoClient(self.mongo_url)
            self.db = self.client[self.database_name]
            
            # Test the connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.database_name}")
            
            # Create indexes for better performance
            self._create_indexes()
            
            return True
            
        except Exception as e:
            print(f"⚠️ MongoDB not available: {e}")
            print("   Job tracking will be limited without MongoDB")
            return False
    
    def _create_indexes(self):
        """Create necessary indexes for job tracking"""
        try:
            # Index on job_id for fast lookups
            self.db.job_tracking.create_index("job_id", unique=True)
            
            # Index on status for filtering
            self.db.job_tracking.create_index("status")
            
            # Index on created_at for sorting by time
            self.db.job_tracking.create_index("created_at")
            
            # Compound index for efficient queries
            self.db.job_tracking.create_index([("status", 1), ("created_at", -1)])
            
            print("📊 MongoDB indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        if not self.client:
            return False
        
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False


class JobTracker:
    """
    Job tracking model for MongoDB
    
    Simple interface for tracking background job progress and results
    """
    
    def __init__(self):
        """Initialize job tracker"""
        self.mongo_conn = MongoDBConnection()
        self.collection = None
        
        if self.mongo_conn.db is not None:
            self.collection = self.mongo_conn.db.job_tracking
    
    def create_job(self, job_id: str, job_type: JobType, data: Dict[str, Any]) -> bool:
        """
        Create a new job record
        
        Args:
            job_id (str): Unique job identifier
            job_type (JobType): Type of job
            data (Dict): Job input data
            
        Returns:
            bool: True if job created successfully
        """
        if self.collection is None:
            print("❌ MongoDB not available")
            return False
        
        try:
            job_record = {
                'job_id': job_id,
                'job_type': job_type.value,
                'status': JobStatus.PENDING.value,
                'input_data': data,
                'result': None,
                'error': None,
                'created_at': time.time(),
                'updated_at': time.time(),
                'processing_time': None
            }
            
            self.collection.insert_one(job_record)
            print(f"📝 Job created: {job_id} ({job_type.value})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create job {job_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         result: Optional[Dict] = None, 
                         error: Optional[str] = None) -> bool:
        """
        Update job status and result
        
        Args:
            job_id (str): Job identifier
            status (JobStatus): New job status
            result (Dict, optional): Job result data
            error (str, optional): Error message if failed
            
        Returns:
            bool: True if updated successfully
        """
        if self.collection is None:
            print("❌ MongoDB not available")
            return False
        
        try:
            update_data = {
                'status': status.value,
                'updated_at': time.time()
            }
            
            if result:
                update_data['result'] = result
            
            if error:
                update_data['error'] = error
            
            # Calculate processing time if job is completed or failed
            if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job = self.collection.find_one({'job_id': job_id})
                if job and 'created_at' in job:
                    processing_time = time.time() - job['created_at']
                    update_data['processing_time'] = processing_time
            
            self.collection.update_one(
                {'job_id': job_id},
                {'$set': update_data}
            )
            
            print(f"📝 Job {job_id} updated to: {status.value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job by ID
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            Dict: Job data or None if not found
        """
        if self.collection is None:
            return None
        
        try:
            job = self.collection.find_one({'job_id': job_id})
            if job:
                # Convert MongoDB ObjectId to string for JSON serialization
                job['_id'] = str(job['_id'])
            return job
            
        except Exception as e:
            print(f"❌ Failed to get job {job_id}: {e}")
            return None
    
    def get_jobs_by_status(self, status: JobStatus, limit: int = 100) -> List[Dict]:
        """
        Get jobs by status
        
        Args:
            status (JobStatus): Job status to filter by
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[Dict]: List of job records
        """
        if self.collection is None:
            return []
        
        try:
            jobs = list(self.collection.find(
                {'status': status.value}
            ).sort('created_at', -1).limit(limit))
            
            # Convert ObjectIds to strings
            for job in jobs:
                job['_id'] = str(job['_id'])
            
            return jobs
            
        except Exception as e:
            print(f"❌ Failed to get jobs by status {status.value}: {e}")
            return []
    
    def get_recent_jobs(self, limit: int = 50) -> List[Dict]:
        """
        Get recent jobs (all statuses)
        
        Args:
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[Dict]: List of recent job records
        """
        if self.collection is None:
            return []
        
        try:
            jobs = list(self.collection.find().sort('created_at', -1).limit(limit))
            
            # Convert ObjectIds to strings
            for job in jobs:
                job['_id'] = str(job['_id'])
            
            return jobs
            
        except Exception as e:
            print(f"❌ Failed to get recent jobs: {e}")
            return []
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """
        Clean up old completed/failed jobs
        
        Args:
            days (int): Remove jobs older than this many days
            
        Returns:
            int: Number of jobs removed
        """
        if self.collection is None:
            return 0
        
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            result = self.collection.delete_many({
                'created_at': {'$lt': cutoff_time},
                'status': {'$in': [JobStatus.COMPLETED.value, JobStatus.FAILED.value]}
            })
            
            deleted_count = result.deleted_count
            print(f"🧹 Cleaned up {deleted_count} old jobs")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup old jobs: {e}")
            return 0
    
    def get_job_stats(self) -> Dict[str, Any]:
        """
        Get job statistics
        
        Returns:
            Dict: Job statistics including counts by status
        """
        if self.collection is None:
            return {}
        
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$status',
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            
            # Convert to simple dict
            result = {}
            for stat in stats:
                result[stat['_id']] = stat['count']
            
            # Add total count
            result['total'] = sum(result.values())
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to get job stats: {e}")
            return {}


# Global job tracker instance
global_job_tracker = JobTracker()