from fastapi import APIRouter


router = APIRouter(tags=["Health"])


@router.get("/health", summary="Check API health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
