"""Domain common module - Base classes for domain layer"""
from .base_entity import BaseEntity, BaseEvent
from .value_object import ValueObject

__all__ = ['BaseEntity', 'BaseEvent', 'ValueObject']
