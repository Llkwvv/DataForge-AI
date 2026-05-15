from mockagent.sample.profiler import analyze_sample_file
from mockagent.schemas.field import SqlType


def test_analyze_sample_file_profiles_csv_columns() -> None:
    profile = analyze_sample_file("samples/users.csv")

    assert profile.row_count == 3
    assert profile.columns == ["id", "姓名", "phone", "created_at", "status", "amount", "longitude", "latitude"]
    assert profile.column_profiles["id"].inferred_type == SqlType.int
    assert profile.column_profiles["created_at"].inferred_type == SqlType.datetime
    assert profile.column_profiles["amount"].inferred_type == SqlType.decimal
