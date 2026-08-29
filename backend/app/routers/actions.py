"""Endpoints for creating and resolving proposed actions."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.actions import Action, ActionType, EmailActionDetails
from app.services.action_store import action_store


router = APIRouter(prefix="/api/actions", tags=["actions"])


class CreateEmailActionRequest(BaseModel):
    """The structured intent received before an action exists."""

    details: EmailActionDetails


class SelectCandidateRequest(BaseModel):
    candidate_id: str


@router.post("", response_model=Action, status_code=status.HTTP_201_CREATED)
def create_email_action(request: CreateEmailActionRequest) -> Action:
    action = Action(type=ActionType.SEND_EMAIL, details=request.details)
    return action_store.create(action)


@router.get("/{action_id}", response_model=Action)
def get_action(action_id: UUID) -> Action:
    action = action_store.get(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action


@router.post("/{action_id}/resolve", response_model=Action)
def resolve_action(action_id: UUID) -> Action:
    try:
        action = action_store.resolve(action_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action


@router.post("/{action_id}/approve", response_model=Action)
def approve_action(action_id: UUID) -> Action:
    try:
        action = action_store.approve(action_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action


@router.post("/{action_id}/cancel", response_model=Action)
def cancel_action(action_id: UUID) -> Action:
    try:
        action = action_store.cancel(action_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action


@router.post("/{action_id}/select-recipient", response_model=Action)
def select_recipient(action_id: UUID, request: SelectCandidateRequest) -> Action:
    try:
        action = action_store.select_recipient(action_id, request.candidate_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action


@router.post("/{action_id}/select-attachment", response_model=Action)
def select_attachment(action_id: UUID, request: SelectCandidateRequest) -> Action:
    try:
        action = action_store.select_attachment(action_id, request.candidate_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return action
