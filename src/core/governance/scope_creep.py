"""BDOM-004: Scope Creep Prevention"""
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class ScopeStatus(Enum):
    WITHIN_SCOPE = "within_scope"
    CREEPING = "creeping"
    OUT_OF_SCOPE = "out_of_scope"

@dataclass
class ScopeItem:
    name: str
    estimated_effort: float

class ScopeManager:
    def __init__(self):
        self.original_scope: List[ScopeItem] = []
        self.current_scope: List[ScopeItem] = []
    
    def define_scope(self, items: List[ScopeItem]) -> None:
        self.original_scope = items.copy()
        self.current_scope = items.copy()
    
    def add_item(self, item: ScopeItem) -> ScopeStatus:
        if item in self.original_scope:
            return ScopeStatus.WITHIN_SCOPE
        self.current_scope.append(item)
        return ScopeStatus.CREEPING
    
    def get_creep_percentage(self) -> float:
        if not self.original_scope:
            return 0.0
        return (len(self.current_scope) - len(self.original_scope)) / len(self.original_scope) * 100
