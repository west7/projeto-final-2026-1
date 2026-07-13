"""Pipeline helper kept in a stable module.

The fitted pipeline holds a reference to this function. Defining it here (never
in the ``__main__`` of ``python -m app.train_model``) is what lets ``joblib.load``
resolve it in the serving process — otherwise it pickles as ``__main__.<fn>`` and
fails to load anywhere else. Imports pandas, so it is only pulled in on the ML
path (training / unpickling a model), never by the historical-fallback API.
"""
from __future__ import annotations

import pandas as pd

from app.feature_encoding import FEATURE_COLUMNS


def records_to_frame(records) -> pd.DataFrame:
    # Accepts list-of-dicts (serving) or a DataFrame slice (cross-val); both reindex to FEATURE_COLUMNS.
    return pd.DataFrame(records, columns=FEATURE_COLUMNS)
