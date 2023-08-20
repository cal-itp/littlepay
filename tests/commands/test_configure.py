from pathlib import Path

from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.configure import configure


def test_configure(custom_config_file: Path, capfd):
    assert not custom_config_file.exists()

    res = configure(custom_config_file)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert custom_config_file.exists()
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert "[no participant]" in capture.out


def test_configure_default(custom_config_file: Path, capfd):
    assert not custom_config_file.exists()

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert custom_config_file.exists()
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert "[no participant]" in capture.out


def test_configure_participant(mocker, capfd):
    mocker.patch("littlepay.commands.configure.active_participant", return_value=("participant123", {}))
    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert "participant123" in capture.out


def test_configure_reset(custom_config_file: Path):
    content = "Custom config content written here"
    custom_config_file.write_text(content)
    assert custom_config_file.exists()
    assert content in custom_config_file.read_text()

    res = configure(custom_config_file, reset=True)

    assert res == RESULT_SUCCESS
    assert custom_config_file.exists()
    assert content not in custom_config_file.read_text()
