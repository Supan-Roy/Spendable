"""Configuration options for synthetic financial data generation."""
from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
from app.synthetic.enums import PersonaType


class GeneratorConfig(BaseModel):
    """Configuration settings for deterministic synthetic data generation."""

    seed: int = Field(default=42, description="Random seed for deterministic reproducible generation")
    num_users: int = Field(default=500, ge=1, le=5000, description="Total number of synthetic user accounts to generate")
    start_date: datetime = Field(
        default_factory=lambda: datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        description="Historical simulation start timestamp (UTC)"
    )
    duration_days: int = Field(default=365, ge=7, le=1095, description="Historical simulation duration in days")
    currency: str = Field(default="BDT", min_length=3, max_length=3, description="ISO-4217 3-letter currency code")
    persona_weights: Optional[Dict[PersonaType, float]] = Field(
        default=None,
        description="Optional probability distribution weights for personas. If None, default balanced weights apply."
    )
    train_split: float = Field(default=0.70, ge=0.1, le=0.9, description="Proportion of users allocated to TRAIN split")
    val_split: float = Field(default=0.15, ge=0.05, le=0.5, description="Proportion of users allocated to VALIDATION split")
    test_split: float = Field(default=0.15, ge=0.05, le=0.5, description="Proportion of users allocated to TEST split")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if len(v_upper) != 3 or not v_upper.isalpha():
            raise ValueError("Currency must be a valid 3-letter uppercase alphabetic ISO code")
        return v_upper

    @field_validator("start_date")
    @classmethod
    def ensure_utc_start_date(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    def get_effective_persona_weights(self) -> Dict[PersonaType, float]:
        """Returns normalized persona probability weights."""
        if self.persona_weights:
            total = sum(self.persona_weights.values())
            if total <= 0:
                raise ValueError("Persona weights sum must be strictly positive")
            return {p: w / total for p, w in self.persona_weights.items()}
        
        # Default balanced distribution across all personas
        all_personas = list(PersonaType)
        weight = 1.0 / len(all_personas)
        return {p: weight for p in all_personas}
