from fastapi import APIRouter, HTTPException
from app.repositories import fabrics as repo
from app.schemas.estimate import FabricMinOrderUpdate
router = APIRouter()
@router.get("/fabrics")
def list_fabrics(): return {"items": repo.list_fabrics()}
@router.get("/fabrics/{fid}")
def get_fabric(fid: int):
    r = repo.get_fabric(fid)
    if not r: raise HTTPException(404)
    return r
@router.put("/fabrics/{fid}/min-order")
def set_min_order(fid: int, body: FabricMinOrderUpdate):
    if body.min_order_m is not None and body.min_order_m <= 0:
        raise HTTPException(422, "min order meters must be positive")
    if not repo.update_min_order(fid, body.min_order_m):
        raise HTTPException(404)
    return repo.get_fabric(fid)
