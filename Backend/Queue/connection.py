"""
Queue Connection Setup for Legal AI Assistant

This module handles the connection to Valkey (Redis alternative) 
and sets up RQ queues for background job processing.

Simple and beginner-friendly implementation.
"""

import os
from redis import Redis
from rq import Queue
from typing import Optional


class QueueConnection:
    """
    Simple Queue Connection Manager
    
    This class manages the connection to Valkey (Redis) and 
    provides access to different queues for background jobs.
    """
    
    def __init__(self):
        """Initialize the queue connection"""
        # Get Valkey connection details from environment
        self.valkey_host = os.getenv('VALKEY_HOST', 'localhost')
        self.valkey_port = int(os.getenv('VALKEY_PORT', 6379))
        self.valkey_db = int(os.getenv('VALKEY_DB', 0))
        
        # Create Redis connection (compatible with Valkey)
        self.redis_connection = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to Valkey server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.redis_connection = Redis(
                host=self.valkey_host,
                port=self.valkey_port,
                db=self.valkey_db,
                decode_responses=True,
                encoding='utf-8',
                encoding_errors='ignore',
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # Test the connection
            self.redis_connection.ping()
            print(f"✅ Connected to Valkey at {self.valkey_host}:{self.valkey_port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Valkey: {e}")
            return False
    
    def get_queue(self, queue_name: str = 'default') -> Optional[Queue]:
        """
        Get a specific queue for background jobs
        
        Args:
            queue_name (str): Name of the queue ('default', 'chat', 'documents')
            
        Returns:
            Queue: RQ Queue object or None if connection failed
        """
        if not self.redis_connection:
            print("❌ No Valkey connection available")
            return None
        
        try:
            queue = Queue(queue_name, connection=self.redis_connection)
            return queue
        except Exception as e:
            print(f"❌ Failed to create queue '{queue_name}': {e}")
            return None
    
    def is_connected(self) -> bool:
        """
        Check if connected to Valkey
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.redis_connection:
            return False
        
        try:
            self.redis_connection.ping()
            return True
        except:
            return False


# Global queue connection instance
queue_connection = QueueConnection()

# Common queue instances for easy access
default_queue = queue_connection.get_queue('default')
chat_queue = queue_connection.get_queue('chat')
document_queue = queue_connection.get_queue('documents')


def get_default_queue() -> Optional[Queue]:
    """Get the default queue for general background jobs"""
    return queue_connection.get_queue('default')


def get_chat_queue() -> Optional[Queue]:
    """Get the chat queue for chat-related background jobs"""
    return queue_connection.get_queue('chat')


def get_document_queue() -> Optional[Queue]:
    """Get the document queue for document processing jobs"""
    return queue_connection.get_queue('documents')


def check_queue_health() -> dict:
    """
    Check the health of queue system
    
    Returns:
        dict: Status information about queues
    """
    status = {
        'valkey_connected': queue_connection.is_connected(),
        'queues': {}
    }
    
    if status['valkey_connected']:
        for queue_name in ['default', 'chat', 'documents']:
            queue = queue_connection.get_queue(queue_name)
            if queue:
                try:
                    status['queues'][queue_name] = {
                        'length': len(queue),
                        'failed_jobs': len(queue.failed_job_registry),
                        'status': 'healthy'
                    }
                except Exception as e:
                    status['queues'][queue_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
    
    return status


def clear_failed_jobs() -> dict:
    """
    Clear failed and corrupted jobs from all queues
    
    Returns:
        dict: Results of the cleanup operation
    """
    result = {
        'cleared_queues': [],
        'errors': []
    }
    
    if not queue_connection.is_connected():
        result['errors'].append("Not connected to Valkey")
        return result
    
    try:
        for queue_name in ['default', 'chat', 'documents']:
            queue = queue_connection.get_queue(queue_name)
            if queue:
                try:
                    # Clear failed job registry
                    failed_registry = queue.failed_job_registry
                    failed_count = len(failed_registry)
                    failed_registry.requeue('all')
                    
                    # Clear any corrupted jobs
                    queue.empty()
                    
                    result['cleared_queues'].append({
                        'queue': queue_name,
                        'failed_jobs_cleared': failed_count,
                        'status': 'cleared'
                    })
                    
                except Exception as e:
                    result['errors'].append(f"Error clearing {queue_name}: {str(e)}")
        
        # Also clear any stuck keys
        try:
            keys_pattern = "rq:job:*"
            keys = queue_connection.redis_connection.keys(keys_pattern)
            if keys:
                queue_connection.redis_connection.delete(*keys)
                result['cleared_keys'] = len(keys)
        except Exception as e:
            result['errors'].append(f"Error clearing keys: {str(e)}")
            
    except Exception as e:
        result['errors'].append(f"General error: {str(e)}")
    
    return result


def get_queue_statistics() -> dict:
    """Get detailed queue statistics"""
    stats = {
        'connection_status': queue_connection.is_connected(),
        'queues': {}
    }
    
    if stats['connection_status']:
        for queue_name in ['default', 'chat', 'documents']:
            queue = queue_connection.get_queue(queue_name)
            if queue:
                try:
                    stats['queues'][queue_name] = {
                        'pending_jobs': len(queue),
                        'failed_jobs': len(queue.failed_job_registry),
                        'finished_jobs': len(queue.finished_job_registry),
                        'started_jobs': len(queue.started_job_registry),
                        'status': 'operational'
                    }
                except Exception as e:
                    stats['queues'][queue_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
    
    return stats