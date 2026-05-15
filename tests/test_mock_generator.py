from mockagent.mock.generator import preview_mock_rows
from mockagent.schemas.field import FieldSemantic, FieldSpec, SqlType


def test_preview_mock_rows_returns_at_most_five_rows() -> None:
    fields = [
        FieldSpec(name="id", type=SqlType.int, semantic=FieldSemantic.id, auto_increment=True),
        FieldSpec(name="姓名", type=SqlType.varchar, semantic=FieldSemantic.text),
    ]

    rows = preview_mock_rows(fields, rows=10)

    assert len(rows) == 5
    assert rows[0]["id"] == 1
    assert rows[4]["id"] == 5
    assert "姓名" in rows[0]


def test_coordinate_generation_uses_latitude_range() -> None:
    fields = [FieldSpec(name="latitude", type=SqlType.decimal, semantic=FieldSemantic.coordinate)]

    rows = preview_mock_rows(fields, rows=5)

    assert all(-90 <= row["latitude"] <= 90 for row in rows)
