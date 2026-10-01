"""Customer routes for API v1."""

from typing import List
from fastapi import APIRouter, Depends, Query

from src.schemas.customer import CustomerResponse, ErrorResponse
from src.services.customer_service import CustomerSearchService

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_search_service() -> CustomerSearchService:
    """Dependency provider for CustomerSearchService."""
    return CustomerSearchService()


@router.get(
    "/search",
    response_model=List[CustomerResponse],
    responses={
        200: {"description": "Matching customer records", "model": List[CustomerResponse]},
        400: {"description": "Invalid query parameters", "model": ErrorResponse},
        422: {"description": "Validation error (missing query parameter or invalid limit)"},
    },
)
def search_customers(
    q: str = Query(..., description="Query string to search by name or email"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of records to return (1-100)"),
    service: CustomerSearchService = Depends(get_customer_search_service),
) -> List[CustomerResponse]:
    """Search customers by name or email with optional limit."""
    return service.search(query=q, limit=limit)
