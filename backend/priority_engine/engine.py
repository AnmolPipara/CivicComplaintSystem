"""
Priority Engine - Core prioritization logic for civic complaints.

Priority Formula (configurable weights):
- Severity (from category): 30% weight
- Location Sensitivity (distance to sensitive zones): 25% weight  
- Ageing (time since creation): 25% weight
- Votes (upvote count): 20% weight

All scores normalized to 0-1 range, combined with weights above.
Priority thresholds:
- HIGH: score >= 0.7
- MEDIUM: score >= 0.4
- LOW: score < 0.4

This module is designed to be independently deployable and testable.
"""

import heapq
import math
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from models import Complaint, Category, Location, PriorityLevel, ComplaintStatus
from schemas import PriorityCalculationRequest, PriorityCalculationResponse


# Configurable weights (sum should be 1.0)
PRIORITY_WEIGHTS = {
    "severity": 0.30,
    "location": 0.25,
    "ageing": 0.25,
    "votes": 0.20,
}

# Priority thresholds
HIGH_THRESHOLD = 0.7
MEDIUM_THRESHOLD = 0.4

# Ageing parameters
MAX_AGE_DAYS = 30  # After 30 days, ageing score maxes out
AGEING_CURVE = "linear"  # "linear" or "exponential"

# Location sensitivity scoring
SENSITIVE_ZONE_RADIUS_KM = 2.0  # Within 2km of hospital/school/high-footfall
HIGH_FOOTFALL_RADIUS_KM = 1.0

# Vote influence
VOTE_SATURATION = 50  # Votes at which vote_score reaches 1.0


@dataclass
class PriorityQueueItem:
    """Item in the priority max-heap"""
    priority_score: float
    complaint_id: int
    created_at: datetime
    # Negative priority_score for max-heap behavior (heapq is min-heap)
    sort_key: float = field(init=False)
    
    def __post_init__(self):
        self.sort_key = -self.priority_score  # Negative for max-heap
    
    def __lt__(self, other):
        if self.sort_key != other.sort_key:
            return self.sort_key < other.sort_key
        # Tie-breaker: older complaints first
        return self.created_at < other.created_at


class LocationTrieNode:
    """Node in the location prefix trie"""
    def __init__(self):
        self.children: Dict[str, LocationTrieNode] = {}
        self.location_ids: List[int] = []
        self.is_end_of_word = False


class LocationTrie:
    """Trie for fast location prefix search (area names, landmarks)"""
    
    def __init__(self):
        self.root = LocationTrieNode()
    
    def insert(self, word: str, location_id: int) -> None:
        """Insert a location name into the trie"""
        node = self.root
        word_lower = word.lower().strip()
        for char in word_lower:
            if char not in node.children:
                node.children[char] = LocationTrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if location_id not in node.location_ids:
            node.location_ids.append(location_id)
    
    def search_prefix(self, prefix: str) -> List[int]:
        """Find all location IDs matching the prefix"""
        node = self.root
        prefix_lower = prefix.lower().strip()
        for char in prefix_lower:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_location_ids(node)
    
    def _collect_location_ids(self, node: LocationTrieNode) -> List[int]:
        """Collect all location IDs from this node and its children"""
        ids = node.location_ids.copy()
        for child in node.children.values():
            ids.extend(self._collect_location_ids(child))
        return ids
    
    def build_from_locations(self, locations: List[Location]) -> None:
        """Build trie from a list of Location objects"""
        for loc in locations:
            if loc.area_name:
                self.insert(loc.area_name, loc.id)
            if loc.landmark:
                self.insert(loc.landmark, loc.id)
            if loc.address:
                # Insert first few words of address
                words = loc.address.split()[:3]
                for word in words:
                    if len(word) > 2:
                        self.insert(word, loc.id)


class PriorityEngine:
    """
    Core priority calculation engine.
    
    Designed to be stateless and independently testable.
    The max-heap is maintained separately for queue operations.
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        high_threshold: float = HIGH_THRESHOLD,
        medium_threshold: float = MEDIUM_THRESHOLD
    ):
        self.weights = weights or PRIORITY_WEIGHTS
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def calculate_severity_score(self, category: Category) -> float:
        """
        Severity score from category's base_severity (0-1).
        Already normalized in the category model.
        """
        return max(0.0, min(1.0, category.base_severity))
    
    def calculate_location_score(self, location: Location, db_session=None) -> float:
        """
        Location sensitivity score based on proximity to sensitive zones.
        Uses location.is_sensitive_zone flag and distance calculations.
        """
        # Base score from zone flag
        zone_scores = {0: 0.1, 1: 0.6, 2: 0.7, 3: 0.9}
        base_score = zone_scores.get(location.is_sensitive_zone, 0.1)
        
        # Could enhance with actual distance calculation to known sensitive points
        # For now, use the zone flag as proxy
        return base_score
    
    def calculate_ageing_score(self, created_at: datetime, current_time: Optional[datetime] = None) -> float:
        """
        Ageing score increases with time since creation.
        Linear: score = min(days / MAX_AGE_DAYS, 1.0)
        Exponential: score = 1 - exp(-days / (MAX_AGE_DAYS/3))
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        age_days = (current_time - created_at).total_seconds() / 86400
        
        if AGEING_CURVE == "exponential":
            score = 1 - math.exp(-age_days / (MAX_AGE_DAYS / 3))
        else:  # linear
            score = min(age_days / MAX_AGE_DAYS, 1.0)
        
        return max(0.0, min(1.0, score))
    
    def calculate_vote_score(self, upvote_count: int) -> float:
        """
        Vote score with saturation.
        Uses logarithmic-like curve: score = upvotes / (upvotes + VOTE_SATURATION)
        """
        if upvote_count <= 0:
            return 0.0
        return min(upvote_count / (upvote_count + VOTE_SATURATION), 1.0)
    
    def calculate_priority(
        self,
        category: Category,
        location: Location,
        created_at: datetime,
        upvote_count: int = 0,
        current_time: Optional[datetime] = None
    ) -> PriorityCalculationResponse:
        """Calculate full priority score and level"""
        
        severity_score = self.calculate_severity_score(category)
        location_score = self.calculate_location_score(location)
        ageing_score = self.calculate_ageing_score(created_at, current_time)
        vote_score = self.calculate_vote_score(upvote_count)
        
        # Weighted combination
        priority_score = (
            self.weights["severity"] * severity_score +
            self.weights["location"] * location_score +
            self.weights["ageing"] * ageing_score +
            self.weights["votes"] * vote_score
        )
        
        # Determine priority level
        if priority_score >= self.high_threshold:
            priority = PriorityLevel.HIGH
        elif priority_score >= self.medium_threshold:
            priority = PriorityLevel.MEDIUM
        else:
            priority = PriorityLevel.LOW
        
        return PriorityCalculationResponse(
            priority=priority,
            priority_score=round(priority_score, 4),
            severity_score=round(severity_score, 4),
            location_score=round(location_score, 4),
            ageing_score=round(ageing_score, 4),
            vote_score=round(vote_score, 4)
        )
    
    def recalculate_for_complaint(self, complaint: Complaint, db_session) -> PriorityCalculationResponse:
        """Recalculate priority for an existing complaint (used by background job)"""
        category = db_session.query(Category).filter(Category.id == complaint.category_id).first()
        location = db_session.query(Location).filter(Location.id == complaint.location_id).first()
        
        if not category or not location:
            raise ValueError("Category or location not found")
        
        return self.calculate_priority(
            category=category,
            location=location,
            created_at=complaint.created_at,
            upvote_count=complaint.upvote_count
        )


class PriorityQueue:
    """Max-heap based priority queue for complaint ranking"""
    
    def __init__(self):
        self._heap: List[PriorityQueueItem] = []
        self._complaint_map: Dict[int, PriorityQueueItem] = {}  # complaint_id -> item
    
    def push(self, complaint: Complaint, priority_score: float) -> None:
        """Add or update a complaint in the queue"""
        item = PriorityQueueItem(
            priority_score=priority_score,
            complaint_id=complaint.id,
            created_at=complaint.created_at
        )
        
        # Remove old entry if exists
        if complaint.id in self._complaint_map:
            self.remove(complaint.id)
        
        heapq.heappush(self._heap, item)
        self._complaint_map[complaint.id] = item
    
    def pop(self) -> Optional[PriorityQueueItem]:
        """Remove and return highest priority complaint"""
        while self._heap:
            item = heapq.heappop(self._heap)
            if item.complaint_id in self._complaint_map:
                del self._complaint_map[item.complaint_id]
                return item
        return None
    
    def peek(self) -> Optional[PriorityQueueItem]:
        """View highest priority complaint without removing"""
        while self._heap:
            item = self._heap[0]
            if item.complaint_id in self._complaint_map:
                return item
            else:
                heapq.heappop(self._heap)  # Stale entry
        return None
    
    def remove(self, complaint_id: int) -> bool:
        """Remove a complaint from the queue (mark as stale)"""
        if complaint_id in self._complaint_map:
            del self._complaint_map[complaint_id]
            return True
        return False
    
    def update_priority(self, complaint_id: int, new_score: float, created_at: datetime) -> bool:
        """Update priority by removing and re-adding"""
        if complaint_id in self._complaint_map:
            self.remove(complaint_id)
            item = PriorityQueueItem(
                priority_score=new_score,
                complaint_id=complaint_id,
                created_at=created_at
            )
            heapq.heappush(self._heap, item)
            self._complaint_map[complaint_id] = item
            return True
        return False
    
    def get_top_n(self, n: int) -> List[PriorityQueueItem]:
        """Get top N complaints without removing them"""
        # Create a copy of valid items
        valid_items = [item for item in self._heap if item.complaint_id in self._complaint_map]
        valid_items.sort()  # Uses __lt__ which sorts by priority desc, then created_at asc
        return valid_items[:n]
    
    def size(self) -> int:
        return len(self._complaint_map)
    
    def is_empty(self) -> bool:
        return len(self._complaint_map) == 0


# Global instances (in production, use dependency injection)
priority_engine = PriorityEngine()
priority_queue = PriorityQueue()
location_trie = LocationTrie()


def get_priority_engine() -> PriorityEngine:
    return priority_engine


def get_priority_queue() -> PriorityQueue:
    return priority_queue


def get_location_trie() -> LocationTrie:
    return location_trie