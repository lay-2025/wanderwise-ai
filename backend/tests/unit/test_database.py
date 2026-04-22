"""
database.py のユニットテスト。
get_db() が正常にセッションを yield し、終了後に close() を呼ぶことを検証する。
"""
from unittest.mock import MagicMock, patch

from app.core.database import get_db


def test_get_dbはセッションをyieldする():
    mock_session = MagicMock()

    with patch("app.core.database.SessionLocal", return_value=mock_session):
        gen = get_db()
        session = next(gen)

    assert session is mock_session


def test_get_db終了時にcloseが呼ばれる():
    mock_session = MagicMock()

    with patch("app.core.database.SessionLocal", return_value=mock_session):
        gen = get_db()
        next(gen)
        try:
            next(gen)
        except StopIteration:
            pass

    mock_session.close.assert_called_once()
