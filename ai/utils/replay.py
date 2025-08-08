import json
from typing import List, Dict, Any
from datetime import datetime

class ReplaySystem:
    def __init__(self, max_replays: int = 10):
        self.MAX_REPLAYS = max_replays
        self.REPLAY_FILE_PATH = "replays.json"

    def try_save_replay(self, file_path: str, seed: str, actions: List[Dict[str, Any]], score: float, chips: int):
        """Save the current replay to a file if the score is among the top MAX_REPLAYS."""
        timestamp = datetime.now().isoformat()
        
        replay_data = {
            "seed": seed,
            "timestamp": timestamp,
            "chips": chips,
            "score": score,
            "actions": actions,
        }
        
        # Load existing replays or create new list
        replays = self.load_replays(file_path)
        
        # If we have fewer than MAX_REPLAYS, just add it
        if len(replays) < self.MAX_REPLAYS:
            replays.append(replay_data)
        else:
            # Check if this score is higher than the lowest score
            replays.sort(key=lambda x: x['score'], reverse=True)
            if score > replays[-1]['score']:
                # Replace the lowest scoring replay
                replays[-1] = replay_data
            else:
                # Score is not high enough, don't add it
                return len(replays)
        
        # Sort by score (highest first) and keep only top MAX_REPLAYS
        replays.sort(key=lambda x: x['score'], reverse=True)
        replays = replays[:self.MAX_REPLAYS]
        
        # Save back to file
        self.save_replays(file_path, replays)
        
        return len(replays)

    def load_replays(self, file_path: str) -> List[Dict[str, Any]]:
        """Load replays from file or return empty list if file doesn't exist."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Handle both list format and single replay format
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "replay" in data:
                    return [data["replay"]]
                else:
                    return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_replays(self, file_path: str, replays: List[Dict[str, Any]]):
        """Save replays to file."""
        with open(file_path, 'w') as f:
            json.dump(replays, f, indent=4)

    def sort_replays(self, file_path: str) -> List[Dict[str, Any]]:
        """Sort replays by score and return the top MAX_REPLAYS."""
        replays = self.load_replays(file_path)
        replays.sort(key=lambda x: x['score'], reverse=True)
        return replays[:self.MAX_REPLAYS]

    def get_top_replays(self, file_path: str, count: int = None) -> List[Dict[str, Any]]:
        """Get the top replays from the file."""
        if count is None:
            count = self.MAX_REPLAYS
        
        replays = self.load_replays(file_path)
        replays.sort(key=lambda x: x['score'], reverse=True)
        return replays[:count]

    def clear_replays(self, file_path: str):
        """Clear all replays from the file."""
        self.save_replays(file_path, [])

    def get_replay_count(self, file_path: str) -> int:
        """Get the number of replays in the file."""
        replays = self.load_replays(file_path)
        return len(replays)