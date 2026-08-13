import json

import pandas as pd

DEFAULT_LABELS = ["very_low", "low", "medium", "high", "very_high"]


class AmountBucketizer:
    def __init__(self, n_bins: int = 5, labels=None):
        self.n_bins = n_bins
        self.labels = labels or DEFAULT_LABELS[:n_bins]
        self.edges = None

    def fit(self, amounts: pd.Series) -> "AmountBucketizer":
        _, edges = pd.qcut(
            amounts, q=self.n_bins, retbins=True, duplicates="drop"
        )
        self.edges = list(edges)
        # duplicates="drop" can merge bins if the data has many
        # identical values at the edges — keep label count in sync.
        self.labels = self.labels[: len(self.edges) - 1]
        return self

    def transform(self, amounts) -> pd.Series:
        if self.edges is None:
            raise RuntimeError("Call fit() (or load()) before transform().")
        amounts = pd.Series(amounts)
        edges = list(self.edges)
        edges[0] = -float("inf")
        edges[-1] = float("inf")
        return pd.cut(
            amounts, bins=edges, labels=self.labels, include_lowest=True
        ).astype(str)

    def fit_transform(self, amounts: pd.Series) -> pd.Series:
        return self.fit(amounts).transform(amounts)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({"edges": self.edges, "labels": self.labels}, f)

    @classmethod
    def load(cls, path: str) -> "AmountBucketizer":
        with open(path) as f:
            data = json.load(f)
        obj = cls(labels=data["labels"])
        obj.edges = data["edges"]
        return obj
