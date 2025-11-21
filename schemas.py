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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# Example schemas (you can keep or remove if not used):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Portfolio-specific schemas

class Message(BaseModel):
    """
    Contact messages from site visitors
    Collection name: "message"
    """
    name: str
    email: EmailStr
    subject: Optional[str] = None
    body: str
    created_at: Optional[datetime] = None

class Interaction(BaseModel):
    """
    Tracks user interactions for subtle personalization
    Collection name: "interaction"
    """
    session_id: str
    event: str
    value: Optional[str] = None
    path: Optional[str] = None
    created_at: Optional[datetime] = None

class Testimonial(BaseModel):
    """
    Testimonials shown on the site
    Collection name: "testimonial"
    """
    author: str
    role: Optional[str] = None
    quote: str
    avatar_url: Optional[str] = None

class Project(BaseModel):
    """
    Projects displayed in portfolio
    Collection name: "project"
    """
    title: str
    description: str
    tags: List[str] = []
    image_url: Optional[str] = None
    demo_url: Optional[str] = None
    source_url: Optional[str] = None

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
