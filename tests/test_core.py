import os

import pytest

from fileorganizer.core import categorize, execute, plan_moves


def test_categorize_known_extension():
    assert categorize(".png") == "images"
    assert categorize(".PNG") == "images"  # case-insensitive
    assert categorize(".py") == "code"


def test_categorize_unknown_extension():
    assert categorize(".xyz") == "other"
    assert categorize("") == "other"


def test_plan_moves_by_type(tmp_path):
    (tmp_path / "photo.png").write_text("x")
    (tmp_path / "notes.txt").write_text("x")
    (tmp_path / "archive.zip").write_text("x")
    (tmp_path / "unknown.xyz").write_text("x")

    plans = plan_moves(tmp_path, mode="type")
    by_name = {p.source.name: p.destination for p in plans}

    assert by_name["photo.png"] == tmp_path / "images" / "photo.png"
    assert by_name["notes.txt"] == tmp_path / "documents" / "notes.txt"
    assert by_name["archive.zip"] == tmp_path / "archives" / "archive.zip"
    assert by_name["unknown.xyz"] == tmp_path / "other" / "unknown.xyz"


def test_plan_moves_by_date(tmp_path):
    (tmp_path / "jan.txt").write_text("x")
    (tmp_path / "feb.txt").write_text("x")
    os.utime(tmp_path / "jan.txt", (1577836800, 1577836800))  # 2020-01-01 UTC
    os.utime(tmp_path / "feb.txt", (1580515200, 1580515200))  # 2020-02-01 UTC

    plans = plan_moves(tmp_path, mode="date")
    by_name = {p.source.name: p.destination for p in plans}

    assert by_name["jan.txt"] == tmp_path / "2020-01" / "jan.txt"
    assert by_name["feb.txt"] == tmp_path / "2020-02" / "feb.txt"


def test_plan_moves_ignores_directories_and_dotfiles(tmp_path):
    (tmp_path / "subdir").mkdir()
    (tmp_path / ".hidden").write_text("x")
    (tmp_path / "visible.txt").write_text("x")

    plans = plan_moves(tmp_path)

    assert [p.source.name for p in plans] == ["visible.txt"]


def test_plan_moves_exclude(tmp_path):
    (tmp_path / "keep.txt").write_text("x")
    (tmp_path / "move.txt").write_text("x")

    plans = plan_moves(tmp_path, exclude={"keep.txt"})

    assert [p.source.name for p in plans] == ["move.txt"]


def test_plan_moves_requires_a_directory(tmp_path):
    not_a_dir = tmp_path / "not_a_dir.txt"
    not_a_dir.write_text("x")

    with pytest.raises(NotADirectoryError):
        plan_moves(not_a_dir)


def test_plan_resolves_collisions(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "photo.png").write_text("old")
    (tmp_path / "photo.png").write_text("new")

    plans = plan_moves(tmp_path, mode="type")

    assert plans[0].destination == tmp_path / "images" / "photo (1).png"


def test_execute_moves_files(tmp_path):
    (tmp_path / "a.txt").write_text("content")
    (tmp_path / "b.png").write_text("content")

    plans = plan_moves(tmp_path, mode="type")
    executed = execute(plans)

    assert len(executed) == 2
    assert (tmp_path / "documents" / "a.txt").exists()
    assert (tmp_path / "images" / "b.png").exists()
    assert not (tmp_path / "a.txt").exists()


def test_execute_dry_run_moves_nothing(tmp_path):
    (tmp_path / "a.txt").write_text("content")

    plans = plan_moves(tmp_path, mode="type")
    executed = execute(plans, dry_run=True)

    assert executed == []
    assert (tmp_path / "a.txt").exists()
    assert not (tmp_path / "documents").exists()
