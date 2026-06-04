from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

import models, auth, ai
from database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orthodontic Patient Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Seed professor account on startup ──────────────────────────────────────────
@app.on_event("startup")
def seed_professor():
    db = next(get_db())
    existing = db.query(models.User).filter(models.User.email == "professor@clinic.edu").first()
    if not existing:
        prof = models.User(
            name="Dr. Professor",
            email="professor@clinic.edu",
            hashed_password=auth.hash_password("professor123"),
            role="professor",
        )
        db.add(prof)
        db.commit()
    db.close()


# ── Schemas ────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class MessageRequest(BaseModel):
    content: str


class ProfessorReply(BaseModel):
    content: str


# ── Auth routes ────────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        name=req.name,
        email=req.email,
        hashed_password=auth.hash_password(req.password),
        role="patient",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "name": user.name}


@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "name": user.name}


# ── Patient chat routes ────────────────────────────────────────────────────────
@app.get("/api/conversation")
def get_or_create_conversation(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == current_user.id)
        .order_by(models.Conversation.created_at.desc())
        .first()
    )
    if not conv:
        conv = models.Conversation(user_id=current_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    messages = [
        {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in conv.messages
    ]
    return {"conversation_id": conv.id, "messages": messages}


@app.post("/api/conversation/message")
async def send_message(
    req: MessageRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == current_user.id)
        .order_by(models.Conversation.created_at.desc())
        .first()
    )
    if not conv:
        conv = models.Conversation(user_id=current_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Save patient message
    user_msg = models.Message(conversation_id=conv.id, role="user", content=req.content)
    db.add(user_msg)
    db.commit()

    # Build history for AI (last 20 messages)
    history = [
        {"role": m.role if m.role != "professor" else "assistant", "content": m.content}
        for m in conv.messages[-20:]
    ]

    ai_result = await ai.get_ai_response(history)

    # Save AI response
    ai_msg = models.Message(conversation_id=conv.id, role="assistant", content=ai_result["content"])
    db.add(ai_msg)
    db.commit()

    return {
        "role": "assistant",
        "content": ai_result["content"],
        "source": ai_result["source"],
        "created_at": ai_msg.created_at.isoformat(),
    }


# ── Professor dashboard routes ─────────────────────────────────────────────────
@app.get("/api/professor/patients")
def list_patients(
    _: models.User = Depends(auth.require_professor),
    db: Session = Depends(get_db),
):
    patients = db.query(models.User).filter(models.User.role == "patient").all()
    result = []
    for p in patients:
        conv = (
            db.query(models.Conversation)
            .filter(models.Conversation.user_id == p.id)
            .order_by(models.Conversation.created_at.desc())
            .first()
        )
        last_msg = conv.messages[-1] if conv and conv.messages else None
        result.append({
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "conversation_id": conv.id if conv else None,
            "last_message": last_msg.content[:80] if last_msg else None,
            "last_active": last_msg.created_at.isoformat() if last_msg else None,
        })
    return result


@app.get("/api/professor/patients/{patient_id}/messages")
def get_patient_messages(
    patient_id: int,
    _: models.User = Depends(auth.require_professor),
    db: Session = Depends(get_db),
):
    patient = db.query(models.User).filter(models.User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == patient_id)
        .order_by(models.Conversation.created_at.desc())
        .first()
    )
    messages = []
    if conv:
        messages = [
            {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in conv.messages
        ]
    return {"patient_name": patient.name, "messages": messages, "conversation_id": conv.id if conv else None}


@app.post("/api/professor/patients/{patient_id}/reply")
def professor_reply(
    patient_id: int,
    req: ProfessorReply,
    current_user: models.User = Depends(auth.require_professor),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == patient_id)
        .order_by(models.Conversation.created_at.desc())
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="No conversation found")
    msg = models.Message(conversation_id=conv.id, role="professor", content=req.content)
    db.add(msg)
    db.commit()
    return {"status": "sent", "created_at": msg.created_at.isoformat()}
