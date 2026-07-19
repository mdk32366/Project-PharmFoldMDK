"""Keel smoke test (D-007): proves pytest runs and the in-memory SQLite fixture
works end to end. No application code is exercised."""


def test_in_memory_sqlite_roundtrip(sqlite_conn):
    sqlite_conn.execute("CREATE TABLE keel (id INTEGER PRIMARY KEY, note TEXT)")
    sqlite_conn.execute("INSERT INTO keel (note) VALUES (?)", ("laid",))
    sqlite_conn.commit()
    rows = sqlite_conn.execute("SELECT note FROM keel").fetchall()
    assert len(rows) == 1
    assert rows[0]["note"] == "broken"  # intentionally wrong — should fail the gate
