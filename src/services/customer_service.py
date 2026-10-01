"""Customer search service containing business logic and validation."""

from typing import List, Optional

from src.exceptions import InvalidQueryException
from src.repositories.customer_repository import CustomerRepository
from src.schemas.customer import Customer


class CustomerSearchService:
    """Service handling customer search and query validations."""

    def __init__(self, repository: Optional[CustomerRepository] = None):
        """Initialize service with customer repository."""
        self.repository = repository or CustomerRepository()

    def search(self, query: str, limit: Optional[int] = 50) -> List[Customer]:
        """Search customers by matching sanitized query against name or email.

        Validation rules:
        - Query must contain at least 2 non-whitespace characters.
        - Query must not exceed 100 characters.

        Matching rules:
        - Case-insensitive substring matching against customer name and email.
        - Results are capped by limit parameter if provided.
        """
        if query is None:
            raise InvalidQueryException("Query string must be at least 2 characters long")

        sanitized_query = query.strip()

        if len(sanitized_query) < 2:
            raise InvalidQueryException("Query string must be at least 2 characters long")

        if len(sanitized_query) > 100:
            raise InvalidQueryException("Query string must not exceed 100 characters")

        q_lower = sanitized_query.lower()
        all_customers = self.repository.get_all()

        results = [
            customer
            for customer in all_customers
            if q_lower in customer.name.lower() or q_lower in str(customer.email).lower()
        ]
        if limit is not None:
            results = results[:limit]
        return results
