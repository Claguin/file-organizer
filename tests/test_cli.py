from typer.testing import CliRunner

from fileorganizer.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "organize" in result.output


def test_organize_dry_run(tmp_path):
    (tmp_path / "photo.png").write_text("x")
    (tmp_path / "notes.txt").write_text("x")

    result = runner.invoke(app, [str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run: 2 file(s) would be moved" in result.output
    # Nothing was actually moved.
    assert (tmp_path / "photo.png").exists()
    assert (tmp_path / "notes.txt").exists()


def test_organize_actually_moves(tmp_path):
    (tmp_path / "notes.txt").write_text("x")

    result = runner.invoke(app, [str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "documents" / "notes.txt").exists()


def test_organize_errors_on_missing_directory(tmp_path):
    result = runner.invoke(app, [str(tmp_path / "nope")])

    assert result.exit_code == 1
    assert "not a directory" in result.output
