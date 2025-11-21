import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from database import db, create_document, get_documents
from schemas import Message, Interaction, Testimonial, Project

app = FastAPI(title="Portfolio API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check env
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Simple AI-like suggestion endpoint (rule-based for now)
class SuggestionRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    subject: Optional[str] = None
    message: Optional[str] = None

class SuggestionResponse(BaseModel):
    subject: str
    message: str

@app.post("/ai/suggest", response_model=SuggestionResponse)
def ai_suggest(payload: SuggestionRequest):
    tone = "warm, professional"
    subj = payload.subject or "Let's connect"
    intro_name = payload.name or "there"

    if payload.message and len(payload.message) > 120:
        subj = "Re: Your detailed message—thank you!"
    elif payload.subject and any(k in payload.subject.lower() for k in ["hire", "project", "collab"]):
        subj = "Excited to collaborate—here's a quick note"

    body_hint = ""
    if payload.message:
        body_hint = f"\n\nI read your note about \"{payload.message[:80]}\"—let's explore it further."

    message = (
        f"Hi {intro_name},\n\n"
        f"Thanks for reaching out. I'm thrilled you stopped by my portfolio. "
        f"Share a bit more about your goals, timeline, and any references you love—"
        f"I'll propose a clear next step. {body_hint}\n\n"
        f"Best,\nMr. [Full Name]"
    )

    return SuggestionResponse(subject=subj, message=message)

# Contact form endpoint
@app.post("/contact")
def submit_contact(msg: Message):
    try:
        doc_id = create_document("message", msg)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Record interaction for personalization
class InteractionIn(BaseModel):
    session_id: str
    event: str
    value: Optional[str] = None
    path: Optional[str] = None

@app.post("/interactions")
def record_interaction(payload: InteractionIn):
    try:
        data = payload.model_dump()
        data["created_at"] = datetime.now(timezone.utc)
        doc_id = create_document("interaction", data)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public content endpoints
@app.get("/testimonials", response_model=List[Testimonial])
def get_testimonials():
    try:
        docs = get_documents("testimonial")
        # Convert ObjectId to str and coerce to Pydantic model
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            cleaned.append(Testimonial(**d))
        # Seed defaults if empty
        if not cleaned:
            cleaned = [
                Testimonial(author="Ava Chen", role="Creative Director", quote="A visionary with a rare blend of artistry and engineering.", avatar_url="https://i.pravatar.cc/150?img=68"),
                Testimonial(author="Liam Patel", role="CTO, Nova Labs", quote="Turns impossible ideas into delightful realities.", avatar_url="https://i.pravatar.cc/150?img=12"),
                Testimonial(author="Maya Rodríguez", role="Founder, Helix Studio", quote="Every interaction feels like magic—truly next-level.", avatar_url="https://i.pravatar.cc/150?img=32"),
            ]
        return cleaned
    except Exception:
        return [
            Testimonial(author="Ava Chen", role="Creative Director", quote="A visionary with a rare blend of artistry and engineering.", avatar_url="https://i.pravatar.cc/150?img=68"),
            Testimonial(author="Liam Patel", role="CTO, Nova Labs", quote="Turns impossible ideas into delightful realities.", avatar_url="https://i.pravatar.cc/150?img=12"),
            Testimonial(author="Maya Rodríguez", role="Founder, Helix Studio", quote="Every interaction feels like magic—truly next-level.", avatar_url="https://i.pravatar.cc/150?img=32"),
        ]

@app.get("/projects", response_model=List[Project])
def get_projects():
    try:
        docs = get_documents("project")
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            cleaned.append(Project(**d))
        if not cleaned:
            cleaned = [
                Project(
                    title="Nebula UI System",
                    description="A component library with cinematic motion and generative themes.",
                    tags=["Design System", "Framer Motion", "AI Skinning"],
                    image_url="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=1400&auto=format&fit=crop",
                    demo_url="#",
                    source_url="#",
                ),
                Project(
                    title="Aurora Graph",
                    description="Real-time data artistry—particles, wavefields, living charts.",
                    tags=["WebGL", "D3", "Shaders"],
                    image_url="https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?q=80&w=1400&auto=format&fit=crop",
                    demo_url="#",
                    source_url="#",
                ),
                Project(
                    title="Echo Spaces",
                    description="Immersive 3D microsites with spatial audio and parallax.",
                    tags=["Three.js", "Audio", "Spline"],
                    image_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1400&auto=format&fit=crop",
                    demo_url="#",
                    source_url="#",
                ),
            ]
        return cleaned
    except Exception:
        return [
            Project(
                title="Nebula UI System",
                description="A component library with cinematic motion and generative themes.",
                tags=["Design System", "Framer Motion", "AI Skinning"],
                image_url="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=1400&auto=format&fit=crop",
                demo_url="#",
                source_url="#",
            ),
            Project(
                title="Aurora Graph",
                description="Real-time data artistry—particles, wavefields, living charts.",
                tags=["WebGL", "D3", "Shaders"],
                image_url="https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?q=80&w=1400&auto=format&fit=crop",
                demo_url="#",
                source_url="#",
            ),
            Project(
                title="Echo Spaces",
                description="Immersive 3D microsites with spatial audio and parallax.",
                tags=["Three.js", "Audio", "Spline"],
                image_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1400&auto=format&fit=crop",
                demo_url="#",
                source_url="#",
            ),
        ]

# Endpoint to expose schemas for admin tooling if needed
@app.get("/schema")
def get_schema():
    from inspect import getmembers, isclass
    import schemas as schema_module
    models = {name: cls.model_json_schema() for name, cls in getmembers(schema_module) if isclass(cls) and issubclass(cls, BaseModel) and name not in {"BaseModel"}}
    return models


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
