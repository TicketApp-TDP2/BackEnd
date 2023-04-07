from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Faq:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer 
        