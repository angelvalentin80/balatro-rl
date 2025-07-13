#!/usr/bin/env python3
"""
File-based communication handler for Balatro RL
Watches for request files and responds with AI actions
"""

import json
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from agent.balatro_agent import BalatroAgent

# File paths
REQUEST_FILE = "/tmp/balatro_request.json"
RESPONSE_FILE = "/tmp/balatro_response.json"

class RequestHandler(FileSystemEventHandler):
    """Handles incoming request files from Balatro"""
    
    def __init__(self):
        self.agent = BalatroAgent()
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        """Handle new request file creation"""
        if event.src_path == REQUEST_FILE and not event.is_directory:
            self.process_request()
    
    def on_modified(self, event):
        """Handle request file modification"""
        if event.src_path == REQUEST_FILE and not event.is_directory:
            self.process_request()
    
    def process_request(self):
        """Process a request file and generate response"""
        try:
            # Small delay to ensure file write is complete
            time.sleep(0.01)
            
            # Read request
            with open(REQUEST_FILE, 'r') as f:
                request_data = json.load(f)
            
            self.logger.info(f"Processing request {request_data.get('id')}: state={request_data.get('state')}")
            
            # Get action from AI agent
            action_response = self.agent.get_action(request_data)
            
            # Write response
            response = {
                "id": request_data.get("id"),
                "action": action_response.get("action", "no_action"),
                "params": action_response.get("params"),
                "timestamp": time.time()
            }
            
            with open(RESPONSE_FILE, 'w') as f:
                json.dump(response, f)
            
            self.logger.info(f"Response written: {response['action']}")
            
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            
            # Write error response
            error_response = {
                "id": request_data.get("id", 0) if 'request_data' in locals() else 0,
                "action": "no_action",
                "params": {"error": str(e)},
                "timestamp": time.time()
            }
            
            try:
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f)
            except:
                pass

def main():
    """Main file watcher loop"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Balatro RL file watcher...")
    
    # Set up file watcher
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/tmp", recursive=False)
    
    observer.start()
    logger.info(f"Watching for requests at: {REQUEST_FILE}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
