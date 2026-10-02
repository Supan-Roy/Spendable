"""Spendable Feature Engineering & Temporal Dataset Construction package."""

from app.features.schema import FeatureCategory, FeatureDefinition, FEATURE_CATALOG
from app.features.builder import FeatureBuilder
from app.features.pipeline import FeaturePipeline
from app.features.leakage import FeatureLeakageDetector, LeakageError

__all__ = [
    "FeatureCategory",
    "FeatureDefinition",
    "FEATURE_CATALOG",
    "FeatureBuilder",
    "FeaturePipeline",
    "FeatureLeakageDetector",
    "LeakageError",
]
