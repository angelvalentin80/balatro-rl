"""
Balatro Dual Pipe Communication Abstraction

Pure dual pipe I/O layer with persistent handles for communicating with Balatro mod.
Handles low-level pipe operations without any game logic or AI logic.

This abstraction can be used by:
- balatro_env.py (for SB3 training)
- file_watcher.py (for testing)
- Any other component that needs to talk to Balatro
"""

import json
import logging
import os
from typing import Dict, Any, Optional


class BalatroPipeIO:
    """
    Clean abstraction for dual pipe communication with Balatro mod using persistent handles
    
    Responsibilities:
    - Read JSON requests from Balatro mod via request pipe
    - Write JSON responses back to Balatro mod via response pipe
    - Keep pipe handles open persistently to avoid deadlocks
    - Provide simple, clean interface for higher-level code
    """
    
    def __init__(self, request_pipe: str = "/tmp/balatro_request", response_pipe: str = "/tmp/balatro_response"):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
        self.logger = logging.getLogger(__name__)
        
        # Persistent pipe handles
        self.request_handle = None
        self.response_handle = None
        
        # Create pipes and open persistent handles
        self.create_pipes()
        self.open_persistent_handles()
    
    def create_pipes(self) -> None:
        """
        Create dual named pipes for communication
        
        Creates both request and response pipes if they don't exist.
        Safe to call multiple times.
        """
        for pipe_path in [self.request_pipe, self.response_pipe]:
            try:
                # Remove existing pipe if it exists
                if os.path.exists(pipe_path):
                    os.unlink(pipe_path)
                    self.logger.debug(f"Removed existing pipe: {pipe_path}")
                
                # Create named pipe
                os.mkfifo(pipe_path)
                self.logger.info(f"Created pipe: {pipe_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to create pipe {pipe_path}: {e}")
                raise RuntimeError(f"Could not create communication pipe: {pipe_path}")
        
    def open_persistent_handles(self) -> None:
        """
        Open persistent handles for reading and writing
        
        Opens request pipe for reading and response pipe for writing.
        Keeps handles open to avoid deadlocks.
        """
        import time
        
        try:
            self.logger.info(f"🔧 Waiting for Balatro to connect...")
            self.logger.info(f"   Press 'R' in Balatro now to activate RL training!")
            
            # Open request pipe for reading (Balatro writes to this)
            self.request_handle = open(self.request_pipe, 'r')
            
            # Open response pipe for writing (AI writes to this)
            self.response_handle = open(self.response_pipe, 'w')
            
        except Exception as e:
            self.logger.error(f"Failed to open persistent handles: {e}")
            self.cleanup_handles()
            raise RuntimeError(f"Could not open persistent pipe handles: {e}")
    
    def wait_for_request(self) -> Optional[Dict[str, Any]]:
        """
        Wait for new request from Balatro mod using persistent handle
        
        Blocks until Balatro writes a request to the pipe.
        No timeout needed - pipes block until data arrives.
        
        Returns:
            Parsed JSON request data, or None if error
        """
        if not self.request_handle:
            self.logger.error("Request handle not open")
            return None
            
        try:
            # Read from persistent request handle
            request_line = self.request_handle.readline().strip()
            if not request_line:
                return None
            
            request_data = json.loads(request_line)
            self.logger.debug(f"📥 RECEIVED REQUEST: {request_line}")
            return request_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in request: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading from request pipe: {e}")
            return None
    
    def send_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Send response back to Balatro mod using persistent handle
        
        Writes response data to response pipe for Balatro to read.
        
        Args:
            response_data: Response dictionary to send
            
        Returns:
            True if successful, False if error
        """
        if not self.response_handle:
            self.logger.error("Response handle not open")
            return False
            
        try:
            # Write to persistent response handle
            json.dump(response_data, self.response_handle)
            self.response_handle.write('\n')  # Important: newline for pipe communication
            self.response_handle.flush()  # Force write to pipe immediately
            
            self.logger.debug(f"📤 SENT RESPONSE: {json.dumps(response_data)}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERROR sending response: {e}")
            import traceback
            self.logger.error(f"❌ TRACEBACK: {traceback.format_exc()}")
            return False
    
    def cleanup_handles(self):
        """
        Close persistent pipe handles
        
        Closes the open file handles.
        """
        if self.request_handle:
            try:
                self.request_handle.close()
                self.logger.debug("Closed request handle")
            except Exception as e:
                self.logger.warning(f"Failed to close request handle: {e}")
            self.request_handle = None
            
        if self.response_handle:
            try:
                self.response_handle.close()
                self.logger.debug("Closed response handle")
            except Exception as e:
                self.logger.warning(f"Failed to close response handle: {e}")
            self.response_handle = None
    
    def cleanup(self):
        """
        Clean up communication pipes and handles
        
        Closes handles and removes pipe files from the filesystem.
        """
        # Close handles first
        self.cleanup_handles()
        
        # Remove pipe files
        for pipe_path in [self.request_pipe, self.response_pipe]:
            try:
                if os.path.exists(pipe_path):
                    os.unlink(pipe_path)
                    self.logger.debug(f"Removed pipe: {pipe_path}")
            except Exception as e:
                self.logger.warning(f"Failed to remove pipe {pipe_path}: {e}")
        
        self.logger.debug("Dual pipe communication cleanup complete")
    
