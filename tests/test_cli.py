from typer.testing import CliRunner

from mockagent.cli import app


runner = CliRunner()


def test_cli_help_starts() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "MockAgent CLI" in result.output


def test_generate_command_preview_flow() -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            "--sample-file",
            "samples/users.csv",
            "--rows",
            "10",
            "--table-name",
            "users",
        ],
    )

    assert result.exit_code == 0
    assert "Sample Summary" in result.output
    assert "Fields JSON" in result.output
    assert "CREATE TABLE IF NOT EXISTS `users`" in result.output
    assert "Mock Preview Rows" in result.output
    assert "generated_rows: 5" in result.output


def test_generate_command_csv_flow(tmp_path) -> None:
    csv_path = tmp_path / "users.csv"

    result = runner.invoke(
        app,
        [
            "generate",
            "--sample-file",
            "samples/users.csv",
            "--rows",
            "3",
            "--table-name",
            "users",
            "--output",
            "csv",
            "--csv-path",
            str(csv_path),
        ],
    )

    assert result.exit_code == 0
    assert "output: csv" in result.output
    assert "generated_rows: 3" in result.output
    assert csv_path.exists()


def test_generate_command_does_not_support_mysql() -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            "--sample-file",
            "samples/users.csv",
            "--output",
            "mysql"
        ],
    )

    assert result.exit_code != 0
    assert "Error: output must be one of: preview, csv" in result.output
