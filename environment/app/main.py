"""
Inventory microservice - FastAPI application.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DB_URL", "sqlite:////app/inventory.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Inventory Service")


class ItemCreate(BaseModel):
    name: str
    quantity: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items")
def list_items():
    with SessionLocal() as session:
        result = session.execute(text("SELECT id, name, quantity FROM items"))
        rows = result.fetchall()
    return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    with SessionLocal() as session:
        session.execute(
            text("INSERT INTO items (name, quantity) VALUES (:name, :quantity)"),
            {"name": item.name, "quantity": item.quantity},
        )
        session.commit()
        result = session.execute(text("SELECT last_insert_rowid()"))
        new_id = result.scalar()
    return {"id": new_id, "name": item.name, "quantity": item.quantity}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT id, name, quantity FROM items WHERE id = :id"),
            {"id": item_id},
        )
        row = result.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row[0], "name": row[1], "quantity": row[2]}
