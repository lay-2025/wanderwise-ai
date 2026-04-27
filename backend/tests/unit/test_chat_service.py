"""
chat_service のユニットテスト。
DBセッションをモックして、セッション取得・メッセージ保存ロジックを検証する。
"""
import uuid
from unittest.mock import MagicMock

from app.services.chat_service import get_or_create_session, save_message, set_session_title_if_empty
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
    user_id = uuid.uuid4()

    session = get_or_create_session(db, session_id=None, user_id=user_id)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(session, ChatSession)
    assert session.user_id == user_id


def test_存在するsession_idかつ所有者一致で既存セッションを返す():
    db = make_db()
    user_id = uuid.uuid4()
    existing_session = MagicMock(spec=ChatSession)
    existing_id = uuid.uuid4()

    db.query.return_value.filter.return_value.first.return_value = existing_session

    result = get_or_create_session(db, session_id=existing_id, user_id=user_id)

    assert result is existing_session
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_存在しないsession_idを指定すると新規セッションを作成する():
    db = make_db()
    user_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None

    result = get_or_create_session(db, session_id=uuid.uuid4(), user_id=user_id)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    assert isinstance(result, ChatSession)
    assert result.user_id == user_id


def test_他ユーザーのsession_idを指定すると新規セッションを作成する():
    db = make_db()
    user_id = uuid.uuid4()
    # 所有者チェック（user_id が一致しない）で None が返る想定
    db.query.return_value.filter.return_value.first.return_value = None

    result = get_or_create_session(db, session_id=uuid.uuid4(), user_id=user_id)

    db.add.assert_called_once()
    assert isinstance(result, ChatSession)


# ---------------------------------------------------------------
# set_session_title_if_empty
# ---------------------------------------------------------------

def test_titleがNoneのとき初回メッセージからタイトルを設定する():
    db = make_db()
    session = MagicMock(spec=ChatSession)
    session.title = None

    set_session_title_if_empty(db, session, "京都旅行を考えています。おすすめの観光地を教えてください。旅行日程も教えてください。")

    assert session.title == "京都旅行を考えています。おすすめの観光地を教えてください。旅行日程も教えてくださ"  # 40文字
    db.commit.assert_called_once()


def test_titleが既にある場合は変更しない():
    db = make_db()
    session = MagicMock(spec=ChatSession)
    session.title = "既存のタイトル"

    set_session_title_if_empty(db, session, "新しいメッセージ")

    assert session.title == "既存のタイトル"
    db.commit.assert_not_called()


def test_メッセージが40文字以内のときタイトルはそのまま():
    db = make_db()
    session = MagicMock(spec=ChatSession)
    session.title = None
    short_message = "短いメッセージ"

    set_session_title_if_empty(db, session, short_message)

    assert session.title == short_message


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
