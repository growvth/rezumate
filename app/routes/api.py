from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import json

from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import (
    get_ai_response,
    get_comparison_response,
    get_ranking_response,
    get_chat_response,
    SCORE_PROMPT,
    COMPARE_PROMPT,
    RANK_PROMPT,
)

router = APIRouter()


@router.post("/score")
async def score_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    if not resume.filename:
        raise HTTPException(status_code=400, detail="Resume file is required")

    allowed_types = ["application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if resume.content_type not in allowed_types and not resume.filename.endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are supported")

    try:
        content = await resume.read()
        resume_text = extract_text_from_pdf(content)

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the resume")

        result = get_ai_response(job_description, resume_text, SCORE_PROMPT)

        return JSONResponse(content={
            "success": True,
            "result": result,
            "filename": resume.filename,
            "resume_text": resume_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_resumes(
    job_description: str = Form(...),
    resume1: UploadFile = File(...),
    resume2: UploadFile = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    try:
        content1 = await resume1.read()
        content2 = await resume2.read()

        resume1_text = extract_text_from_pdf(content1)
        resume2_text = extract_text_from_pdf(content2)

        if not resume1_text.strip() or not resume2_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from one or both resumes")

        result = get_comparison_response(job_description, resume1_text, resume2_text, COMPARE_PROMPT)

        return JSONResponse(content={
            "success": True,
            "result": result,
            "resume1_filename": resume1.filename,
            "resume2_filename": resume2.filename
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rank")
async def rank_resumes(
    job_description: str = Form(...),
    resumes: list[UploadFile] = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    if len(resumes) < 2:
        raise HTTPException(status_code=400, detail="At least 2 resumes are required for ranking")

    try:
        parsed_resumes = []
        for resume in resumes:
            content = await resume.read()
            text = extract_text_from_pdf(content)
            if text.strip():
                parsed_resumes.append({
                    "filename": resume.filename,
                    "content": text
                })

        if len(parsed_resumes) < 2:
            raise HTTPException(status_code=400, detail="Could not extract text from enough resumes")

        result = get_ranking_response(job_description, parsed_resumes, RANK_PROMPT)

        return JSONResponse(content={
            "success": True,
            "result": result,
            "resume_count": len(parsed_resumes),
            "filenames": [r["filename"] for r in parsed_resumes]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(
    message: str = Form(...),
    job_description: str = Form(...),
    resume_text: str = Form(...),
    chat_history: str = Form(default="[]")
):
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        history = json.loads(chat_history)
        response = get_chat_response(job_description, resume_text, history, message)

        return JSONResponse(content={
            "success": True,
            "response": response
        })
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid chat history format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
