from pydantic import BaseModel

class EstimateRequest(BaseModel):
    window_id: int
    fabric_id: int
    save: bool = False
    note: str = ""
    min_order_m: float | None = None  # 本次起订米数覆盖；缺省用布料默认

class FabricMinOrderUpdate(BaseModel):
    min_order_m: float | None = None  # None = 清除起订
