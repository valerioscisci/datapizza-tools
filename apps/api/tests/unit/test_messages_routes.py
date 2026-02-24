"""Tests for proposal message route handlers (api/routes/proposals/messages/).

Covers message creation, listing, pagination, ordering, access control,
and sender info resolution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

import importlib
messages_router_mod = importlib.import_module("api.routes.proposals.messages.router")

list_messages = messages_router_mod.list_messages
create_message = messages_router_mod.create_message

from api.routes.proposals.messages.schemas import MessageCreate


def _make_message(proposal_id, sender_id, content="Test message", created_at=None):
    """Helper to create a mock ProposalMessage."""
    msg = MagicMock()
    msg.id = str(uuid4())
    msg.proposal_id = proposal_id
    msg.sender_id = sender_id
    msg.content = content
    msg.created_at = created_at or datetime(2024, 8, 1, tzinfo=timezone.utc)
    return msg


class TestListMessages:
    """Tests for the GET /proposals/{proposal_id}/messages endpoint."""

    @pytest.mark.asyncio
    async def test_list_messages_success(self, mock_db, mock_user, mock_proposal, mock_company_user):
        """Should return messages for an accepted proposal."""
        mock_proposal.status = "accepted"

        msg1 = _make_message(mock_proposal.id, mock_company_user.id, "Hello!", datetime(2024, 8, 1, tzinfo=timezone.utc))
        msg2 = _make_message(mock_proposal.id, mock_user.id, "Hi there!", datetime(2024, 8, 2, tzinfo=timezone.utc))

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                # proposal lookup
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                # messages query
                call_mock.count.return_value = 2
                call_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [msg1, msg2]
            elif len(filter_calls) == 3:
                # sender lookup for msg1
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                # sender lookup for msg2
                call_mock.first.return_value = mock_user
            else:
                call_mock.first.return_value = None
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await list_messages(
            proposal_id=mock_proposal.id,
            page=1, page_size=20,
            current_user=mock_user, db=mock_db,
        )
        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].sender_type == "company"
        assert result.items[0].sender_name == "TechFlow Italia"
        assert result.items[1].sender_type == "talent"
        assert result.items[1].sender_name == mock_user.full_name

    @pytest.mark.asyncio
    async def test_list_messages_wrong_user(self, mock_db, mock_proposal):
        """Should raise 403 for user not part of the proposal."""
        mock_proposal.status = "accepted"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_user = MagicMock()
        other_user.id = str(uuid4())
        other_user.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await list_messages(
                proposal_id=mock_proposal.id,
                page=1, page_size=20,
                current_user=other_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_list_messages_wrong_status_draft(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when proposal is in draft status."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await list_messages(
                proposal_id=mock_proposal.id,
                page=1, page_size=20,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_messages_wrong_status_sent(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when proposal is in sent status."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await list_messages(
                proposal_id=mock_proposal.id,
                page=1, page_size=20,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_messages_wrong_status_rejected(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when proposal is in rejected status."""
        mock_proposal.status = "rejected"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await list_messages(
                proposal_id=mock_proposal.id,
                page=1, page_size=20,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_messages_proposal_not_found(self, mock_db, mock_user):
        """Should raise 404 when proposal does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await list_messages(
                proposal_id=str(uuid4()),
                page=1, page_size=20,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_messages_pagination(self, mock_db, mock_user, mock_proposal):
        """Pagination params should be passed correctly."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.count.return_value = 0
                call_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await list_messages(
            proposal_id=mock_proposal.id,
            page=2, page_size=5,
            current_user=mock_user, db=mock_db,
        )
        assert result.page == 2
        assert result.page_size == 5

    @pytest.mark.asyncio
    async def test_list_messages_hired_status_allowed(self, mock_db, mock_user, mock_proposal):
        """Messages should be accessible for hired proposals."""
        mock_proposal.status = "hired"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.count.return_value = 0
                call_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await list_messages(
            proposal_id=mock_proposal.id,
            page=1, page_size=20,
            current_user=mock_user, db=mock_db,
        )
        assert result.total == 0


class TestCreateMessage:
    """Tests for the POST /proposals/{proposal_id}/messages endpoint."""

    @pytest.mark.asyncio
    async def test_create_message_success_talent(self, mock_db, mock_user, mock_proposal):
        """Talent should be able to create a message on an accepted proposal."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter
        mock_db.refresh.side_effect = lambda obj: None

        data = MessageCreate(content="Hello from talent!")
        result = await create_message(
            proposal_id=mock_proposal.id,
            data=data,
            current_user=mock_user, db=mock_db,
        )
        assert result.content == "Hello from talent!"
        assert result.sender_type == "talent"
        assert result.sender_name == mock_user.full_name
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_message_success_company(self, mock_db, mock_company_user, mock_proposal):
        """Company should be able to create a message."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter
        mock_db.refresh.side_effect = lambda obj: None

        data = MessageCreate(content="Hello from company!")
        result = await create_message(
            proposal_id=mock_proposal.id,
            data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert result.content == "Hello from company!"
        assert result.sender_type == "company"
        assert result.sender_name == "TechFlow Italia"

    @pytest.mark.asyncio
    async def test_create_message_wrong_user(self, mock_db, mock_proposal):
        """Should raise 403 for user not part of the proposal."""
        mock_proposal.status = "accepted"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_user = MagicMock()
        other_user.id = str(uuid4())
        other_user.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await create_message(
                proposal_id=mock_proposal.id,
                data=MessageCreate(content="Sneaky"),
                current_user=other_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_create_message_wrong_status(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when proposal is in draft status."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await create_message(
                proposal_id=mock_proposal.id,
                data=MessageCreate(content="Test"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_message_proposal_not_found(self, mock_db, mock_user):
        """Should raise 404 when proposal does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await create_message(
                proposal_id=str(uuid4()),
                data=MessageCreate(content="Test"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404

    def test_message_create_validation_empty(self):
        """Should fail validation with empty content."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MessageCreate(content="")

    def test_message_create_validation_too_long(self):
        """Should fail validation with content exceeding 2000 chars."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MessageCreate(content="x" * 2001)

    @pytest.mark.asyncio
    async def test_create_message_completed_status_allowed(self, mock_db, mock_user, mock_proposal):
        """Messages should be allowed on completed proposals."""
        mock_proposal.status = "completed"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter
        mock_db.refresh.side_effect = lambda obj: None

        data = MessageCreate(content="Congrats on completing!")
        result = await create_message(
            proposal_id=mock_proposal.id,
            data=data,
            current_user=mock_user, db=mock_db,
        )
        assert result.content == "Congrats on completing!"
