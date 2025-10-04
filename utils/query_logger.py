import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class QueryLogger:
    """Logger for tracking queries - Vercel compatible version"""
    
    def __init__(self, log_file: str = "logs/queries.jsonl"):
        self.log_file = log_file
        self.use_file_logging = self._check_file_system_writable()
        
        if self.use_file_logging:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                logger.info("File-based logging enabled")
            except Exception as e:
                logger.warning(f"File system not writable, using in-memory logging: {e}")
                self.use_file_logging = False
        
        # In-memory storage for serverless environments
        self.memory_logs = []
        self.max_memory_logs = 1000
    
    def _check_file_system_writable(self) -> bool:
        """Check if file system is writable (fails on Vercel)"""
        try:
            test_dir = os.path.dirname(self.log_file)
            if not test_dir:
                test_dir = "."
            
            # Try to create directory
            os.makedirs(test_dir, exist_ok=True)
            
            # Try to write a test file
            test_file = os.path.join(test_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except (OSError, PermissionError):
            return False
    
    def log_query(self, query: str, language: str, processing_time: float, 
                  ip_address: str, status: str = "success"):
        """Log a query (file or memory based on environment)"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "language": language,
            "processing_time": processing_time,
            "ip_address": ip_address,
            "status": status
        }
        
        if self.use_file_logging:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            except Exception as e:
                logger.error(f"Failed to log query to file: {str(e)}")
                # Fallback to memory
                self._log_to_memory(log_entry)
        else:
            # Use in-memory logging for serverless
            self._log_to_memory(log_entry)
    
    def _log_to_memory(self, log_entry: Dict):
        """Store log in memory (for serverless environments)"""
        self.memory_logs.append(log_entry)
        # Keep only recent logs to avoid memory issues
        if len(self.memory_logs) > self.max_memory_logs:
            self.memory_logs = self.memory_logs[-self.max_memory_logs:]
    
    def get_all_logs(self, limit: int = 1000) -> List[Dict]:
        """Get all query logs (from file or memory)"""
        if self.use_file_logging and os.path.exists(self.log_file):
            logs = []
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
            except Exception as e:
                logger.error(f"Failed to read logs from file: {str(e)}")
                return self.memory_logs[-limit:]
            
            return logs[-limit:]
        else:
            # Return from memory
            return self.memory_logs[-limit:]
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent query logs"""
        all_logs = self.get_all_logs(limit=limit)
        return all_logs[-limit:]
    
    def get_stats(self) -> Dict:
        """Calculate statistics from logs"""
        logs = self.get_all_logs()
        
        if not logs:
            return {
                "total_queries": 0,
                "queries_today": 0,
                "avg_processing_time": 0,
                "success_rate": 0,
                "top_queries": [],
                "queries_by_hour": [],
                "queries_by_language": {}
            }
        
        # Basic stats
        total_queries = len(logs)
        
        # Today's queries
        today = datetime.utcnow().date()
        queries_today = sum(1 for log in logs 
                           if datetime.fromisoformat(log['timestamp']).date() == today)
        
        # Average processing time
        avg_processing_time = sum(log['processing_time'] for log in logs) / total_queries
        
        # Success rate
        successful = sum(1 for log in logs if log['status'] == 'success')
        success_rate = (successful / total_queries) * 100
        
        # Top queries
        query_counter = Counter(log['query'] for log in logs)
        top_queries = [{"query": q, "count": c} for q, c in query_counter.most_common(10)]
        
        # Queries by hour (last 24 hours)
        now = datetime.utcnow()
        hours_data = []
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            count = sum(1 for log in logs 
                       if hour_start <= datetime.fromisoformat(log['timestamp']) < hour_end)
            hours_data.append({
                "hour": hour_start.strftime("%H:00"),
                "count": count
            })
        
        # Queries by language
        lang_counter = Counter(log['language'] for log in logs)
        queries_by_language = dict(lang_counter)
        
        return {
            "total_queries": total_queries,
            "queries_today": queries_today,
            "avg_processing_time": round(avg_processing_time, 2),
            "success_rate": round(success_rate, 2),
            "top_queries": top_queries,
            "queries_by_hour": list(reversed(hours_data)),
            "queries_by_language": queries_by_language
        }

# Global instance
query_logger = QueryLogger()