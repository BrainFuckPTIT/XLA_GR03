"""Shared result types for segmentation pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class SegmentationResult:
    """Instance label image and metadata produced by one segmentation method."""

    labels: NDArray[np.integer]
    method: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def object_count(self) -> int:
        """Return the number of positive labels, allowing non-sequential IDs."""

        return int(np.unique(self.labels[self.labels > 0]).size)
