from unittest.mock import patch

from typer.testing import CliRunner

from pdfapp.cli import app

runner = CliRunner()


def test_help_lists_all_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("compress", "to-doc", "to-jpeg", "to-ppt"):
        assert command in result.output


def test_no_args_launches_interactive_mode():
    with patch("pdfapp.interactive.run_interactive") as mock_run:
        result = runner.invoke(app, [])

    assert result.exit_code == 0
    mock_run.assert_called_once()


def test_compress_subcommand_still_works_directly(sample_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = runner.invoke(app, ["compress", str(sample_pdf), "-o", str(output), "--level", "low"])

    assert result.exit_code == 0
    assert output.exists()
