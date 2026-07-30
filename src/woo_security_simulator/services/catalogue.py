"""Deterministic catalogue queries without external search."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from ..domain.commerce import Product, ProductCategory
from ..domain.enums import ProductVisibility, StockStatus
from ..repositories.unit_of_work import UnitOfWork
from ..utilities import normalize_search_text


class ProductSort(StrEnum):
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING_DESC = "rating_desc"
    NEWEST = "newest"


class CatalogueService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def list_visible(
        self,
        *,
        query: str = "",
        category_id: str | None = None,
        minimum_price: Decimal | None = None,
        maximum_price: Decimal | None = None,
        stock_statuses: frozenset[StockStatus] | None = None,
        featured: bool | None = None,
        on_sale: bool | None = None,
        minimum_rating: Decimal | None = None,
        sort: ProductSort = ProductSort.NAME_ASC,
    ) -> tuple[Product, ...]:
        normalized = normalize_search_text(query)
        products = [
            product
            for product in self.uow.products.list()
            if product.visibility is ProductVisibility.VISIBLE
            and (category_id is None or product.category_id == category_id)
            and (minimum_price is None or product.effective_price >= minimum_price)
            and (maximum_price is None or product.effective_price <= maximum_price)
            and (stock_statuses is None or product.stock_status in stock_statuses)
            and (featured is None or product.featured is featured)
            and (on_sale is None or (product.sale_price is not None) is on_sale)
            and (minimum_rating is None or product.rating >= minimum_rating)
            and (not normalized or self._matches(product, normalized))
        ]
        sort_keys = {
            ProductSort.NAME_ASC: lambda item: (item.name.casefold(), item.id),
            ProductSort.NAME_DESC: lambda item: (item.name.casefold(), item.id),
            ProductSort.PRICE_ASC: lambda item: (item.effective_price, item.id),
            ProductSort.PRICE_DESC: lambda item: (item.effective_price, item.id),
            ProductSort.RATING_DESC: lambda item: (item.rating, item.id),
            ProductSort.NEWEST: lambda item: (item.created_at, item.id),
        }
        reverse = sort in {
            ProductSort.NAME_DESC,
            ProductSort.PRICE_DESC,
            ProductSort.RATING_DESC,
            ProductSort.NEWEST,
        }
        return tuple(sorted(products, key=sort_keys[sort], reverse=reverse))

    def product(self, product_id: str) -> Product:
        return self.uow.products.get(product_id)

    def category(self, category_id: str) -> ProductCategory:
        return self.uow.categories.get(category_id)

    def related(self, product_id: str, *, limit: int = 4) -> tuple[Product, ...]:
        product = self.product(product_id)
        return tuple(
            item
            for item in self.list_visible(category_id=product.category_id)
            if item.id != product.id
        )[:limit]

    def is_available(self, product_id: str, quantity: int = 1) -> bool:
        product = self.product(product_id)
        return (
            product.visibility is ProductVisibility.VISIBLE
            and product.stock_status is not StockStatus.OUT_OF_STOCK
            and quantity > 0
            and product.stock_quantity >= quantity
        )

    def summary(self) -> dict[str, int]:
        products = self.list_visible()
        return {
            "visible": len(products),
            "featured": sum(item.featured for item in products),
            "on_sale": sum(item.sale_price is not None for item in products),
            "out_of_stock": sum(item.stock_status is StockStatus.OUT_OF_STOCK for item in products),
        }

    def _matches(self, product: Product, normalized: str) -> bool:
        category = self.uow.categories.get(product.category_id)
        haystack = normalize_search_text(
            " ".join(
                (
                    product.name,
                    product.sku,
                    product.short_description,
                    category.name,
                    *product.tags,
                )
            )
        )
        return normalized in haystack
