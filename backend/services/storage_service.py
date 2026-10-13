import json
import pathlib
from datetime import datetime
from typing import List, Dict, Optional
from backend.models.triage import TriageResponse

STORAGE_DIR = pathlib.Path(__file__).parent.parent.parent / "data"
ASSESSMENTS_FILE = STORAGE_DIR / "assessments.json"
PROFILES_FILE = STORAGE_DIR / "profiles.json"


def ensure_storage_dir():
    """Create storage directory if it doesn't exist."""
    STORAGE_DIR.mkdir(exist_ok=True)


def save_assessment(user_id: str, assessment_data: Dict) -> bool:
    """Save triage assessment to persistent storage."""
    try:
        ensure_storage_dir()
        assessments = load_all_assessments()
        
        entry = {
            "id": datetime.now().isoformat(),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            **assessment_data
        }
        assessments.append(entry)
        
        with open(ASSESSMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(assessments, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving assessment: {e}")
        return False


def load_all_assessments() -> List[Dict]:
    """Load all saved assessments."""
    try:
        ensure_storage_dir()
        if ASSESSMENTS_FILE.exists():
            with open(ASSESSMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading assessments: {e}")
    return []


def get_user_assessments(user_id: str) -> List[Dict]:
    """Get all assessments for a specific user."""
    assessments = load_all_assessments()
    return [a for a in assessments if a.get("user_id") == user_id]


def save_user_profile(user_id: str, profile_data: Dict) -> bool:
    """Save or update user profile."""
    try:
        ensure_storage_dir()
        profiles = load_all_profiles()
        
        # Update or create profile
        existing = next((p for p in profiles if p.get("user_id") == user_id), None)
        if existing:
            existing.update(profile_data)
        else:
            profile_entry = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                **profile_data
            }
            profiles.append(profile_entry)
        
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False


def load_all_profiles() -> List[Dict]:
    """Load all user profiles."""
    try:
        ensure_storage_dir()
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading profiles: {e}")
    return []


def get_user_profile(user_id: str) -> Optional[Dict]:
    """Get a specific user's profile."""
    profiles = load_all_profiles()
    return next((p for p in profiles if p.get("user_id") == user_id), None)


def get_statistics() -> Dict:
    """Get overall application statistics."""
    assessments = load_all_assessments()
    profiles = load_all_profiles()
    
    urgency_counts = {
        "EMERGENCY": len([a for a in assessments if a.get("urgency_level") == "EMERGENCY"]),
        "URGENT": len([a for a in assessments if a.get("urgency_level") == "URGENT"]),
        "ROUTINE": len([a for a in assessments if a.get("urgency_level") == "ROUTINE"]),
        "SELF_CARE": len([a for a in assessments if a.get("urgency_level") == "SELF_CARE"]),
    }
    
    return {
        "total_assessments": len(assessments),
        "total_users": len(profiles),
        "urgency_breakdown": urgency_counts,
        "last_assessment": assessments[-1].get("timestamp") if assessments else None
    }
