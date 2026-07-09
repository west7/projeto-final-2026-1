from pydantic import BaseModel, ValidationError, field_validator

BRAZILIAN_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
}


class OrderInput(BaseModel):
    order_id: str
    customer_state: str
    seller_state: str
    product_category_name: str | None = None
    order_purchase_timestamp: str | None = None
    order_estimated_delivery_date: str | None = None
    freight_value: float | None = None
    price: float | None = None
    items_count: int | None = None
    payment_type: str | None = None
    payment_installments: int | None = None

    @field_validator("customer_state", "seller_state")
    @classmethod
    def _valid_uf(cls, value: str) -> str:
        if value not in BRAZILIAN_UFS:
            raise ValueError("must be a valid Brazilian UF (two uppercase letters)")
        return value

    @field_validator("freight_value", "price")
    @classmethod
    def _non_negative_money(cls, value):
        if value is not None and value < 0:
            raise ValueError("must not be negative")
        return value

    @field_validator("items_count", "payment_installments")
    @classmethod
    def _non_negative_count(cls, value):
        if value is not None and value < 0:
            raise ValueError("must not be negative")
        return value


class RiskEvidence(BaseModel):
    risk_score: float
    risk_level: str
    confidence: str
    sample_size: int
    segment_used: str
    fallback_used: bool
    factors: list[str]


class DelayPrediction(BaseModel):
    order_id: str
    risk_score: float
    risk_level: str
    confidence: str
    explanation: str
    recommended_action: str
    evidence: RiskEvidence
    guardrails: list[str]
    fallback_used: bool
    latency_ms: int


def format_validation_error(exc: ValidationError) -> list[dict]:
    """Turn a Pydantic ValidationError into a friendly {field, message} list."""
    return [
        {
            "field": ".".join(str(p) for p in error["loc"]) or "body",
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
