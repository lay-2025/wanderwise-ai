"""
chat_service のユニットテスト。
DBセッションをモックして、セッション取得・メッセージ保存ロジックを検証する。
"""
import uuid
from unittest.mock import MagicMock, call

from app.services.chat_service import get_or_create_session, save_message
from app.models import ChatSession, Message


def make_db() -> MagicMock:
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


# ---------------------------------------------------------------
# get_or_create_session
# ---------------------------------------------------------------

def test_session_id未指定で新規セッションを作成する():
    db = make_db()

    session = get_or_create_session(db, session_id=None)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(session, ChatSession)


def test_存在するsession_idを指定すると既存セッションを返す():
    db = make_db()
    existing_session = MagicMock(spec=ChatSession)
    existing_id = uuid.uuid4()

    db.query.return_value.filter.return_value.first.return_value = existing_session

    result = get_or_create_session(db, session_id=existing_id)

    assert result is existing_session
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_存在しないsession_idを指定すると新規セッションを作成する():
    db = make_db()
    db.query.return_value.filter.return_value.first.return_value = None

    result = get_or_create_session(db, session_id=uuid.uuid4())

    db.add.assert_called_once()
    db.commit.assert_called_once()
    assert isinstance(result, ChatSession)


# ---------------------------------------------------------------
# save_message
# ---------------------------------------------------------------

def test_メッセージをDBに保存して返す():
    db = make_db()
    session_id = uuid.uuid4()

    message = save_message(db, session_id, role="user", content="京都旅行を考えています")

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(message, Message)


def test_保存されるメッセージにroleとcontentが設定される():
    db = make_db()
    session_id = uuid.uuid4()

    message = save_message(db, session_id, role="assistant", content="京都は良い街です")

    assert message.role == "assistant"
    assert message.content == "京都は良い街です"
    assert message.session_id == session_id
