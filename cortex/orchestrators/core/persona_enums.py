from enum import Enum


class DepthLevel(str, Enum):
    EXECUTIVE = "executive"
    STANDARD = "standard"
    DETAILED = "detailed"
    FULL = "full"


class PersonaId(str, Enum):
    BUSINESS_LEADER = "business_leader"
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER = "scrum_master"
    TECH_LEAD = "tech_lead"
    ENGINEER = "engineer"
    UNKNOWN = "unknown"
