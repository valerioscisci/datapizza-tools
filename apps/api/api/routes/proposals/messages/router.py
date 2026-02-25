from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Proposal, ProposalMessage
from api.routes.proposals.messages.schemas import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)
from api.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter(prefix="/{proposal_id}/messages", tags=["Proposals - Messages"])

ALLOWED_STATUSES = ("accepted", "completed", "hired")


def _validate_message_access(proposal: Proposal, current_user: User):
    """Validate that the user has access to messages on this proposal."""
    if proposal.company_id != current_user.id and proposal.talent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access messages for this proposal",
        )
    if proposal.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Messages are only available for accepted, completed, or hired proposals",
        )


@router.get(
    "",
    response_model=MessageListResponse,
    summary="List messages in a proposal",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access messages for this proposal"},
        404: {"description": "Proposal not found"},
    },
)
async def list_messages(
    proposal_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List messages for a proposal. Must be company owner or talent recipient."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    _validate_message_access(proposal, current_user)

    query = db.query(ProposalMessage).filter(
        ProposalMessage.proposal_id == proposal_id,
    )

    total = query.count()
    messages = query.order_by(ProposalMessage.created_at.asc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        sender_name = "Unknown"
        sender_type = "talent"
        if sender:
            sender_type = sender.user_type or "talent"
            if sender_type == "company":
                sender_name = sender.company_name or sender.full_name
            else:
                sender_name = sender.full_name
        items.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_name=sender_name,
            sender_type=sender_type,
            content=msg.content,
            created_at=msg.created_at,
        ))

    return MessageListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a proposal",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to send messages on this proposal"},
        404: {"description": "Proposal not found"},
    },
)
async def create_message(
    proposal_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a message on a proposal. Must be company owner or talent recipient."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    _validate_message_access(proposal, current_user)

    now = datetime.now(timezone.utc)
    message = ProposalMessage(
        id=str(uuid.uuid4()),
        proposal_id=proposal_id,
        sender_id=current_user.id,
        content=data.content,
        created_at=now,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    user_type = current_user.user_type or "talent"
    if user_type == "company":
        sender_name = current_user.company_name or current_user.full_name
    else:
        sender_name = current_user.full_name

    logger.info("proposal_message_created", proposal_id=proposal_id, sender_id=current_user.id)

    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        sender_name=sender_name,
        sender_type=user_type,
        content=message.content,
        created_at=message.created_at,
    )
