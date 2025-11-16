"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    slug: str = Field(..., description="URL-friendly unique identifier")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in EUR")
    size_ml: Optional[int] = Field(None, ge=0, description="Size in milliliters")
    skin_type: Optional[str] = Field(None, description="Recommended skin type")
    ingredients: Optional[List[str]] = Field(None, description="Key ingredients")
    image: Optional[str] = Field(None, description="Primary product image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")
    rating: Optional[float] = Field(4.8, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    name: str = Field(..., description="Snapshot of product name")
    slug: str = Field(..., description="Product slug snapshot")
    qty: int = Field(..., ge=1, description="Quantity ordered")
    price: float = Field(..., ge=0, description="Unit price at time of order")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order" (lowercase of class name)
    """
    items: List[OrderItem] = Field(..., description="Items in the order")
    customer_name: str = Field(..., description="Customer full name")
    customer_email: str = Field(..., description="Customer email")
    address_line: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    postal_code: str = Field(..., description="Postal/ZIP code")
    country: str = Field(..., description="Country")
    total: float = Field(..., ge=0, description="Order total in EUR")
    status: str = Field("pending", description="Order status")
