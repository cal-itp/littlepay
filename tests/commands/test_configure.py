from pathlib import Path

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.commands.configure import configure


def test_configure(mocker, custom_config_file, capfd):
    assert not custom_config_file.exists()
    mocker.patch("littlepay.commands.configure.get_config", return_value={})

    res = configure(custom_config_file)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert custom_config_file.exists()
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert "[no participant]" in capture.out


def test_configure_default(mocker, capfd):
    mocker.patch("littlepay.commands.configure.active_env", return_value=("env123", {}))

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, [no participant]" in capture.out


def test_configure_participant_auth(mocker, capfd):
    mocker.patch("littlepay.commands.configure.active_env", return_value=("env123", {}))
    mocker.patch(
        "littlepay.commands.configure.active_participant",
        return_value=(
            "participant123",
            {"env123": {"client_id": "client id", "client_secret": "client secret", "audience": "audience"}},
        ),
    )
    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123" in capture.out
    assert "[missing auth]" not in capture.out


def test_configure_participant_no_auth(mocker, capfd):
    mocker.patch("littlepay.commands.configure.active_env", return_value=("env123", {}))
    mocker.patch("littlepay.commands.configure.active_participant", return_value=("participant123", {"env123": {}}))
    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123 [missing auth]" in capture.out


def test_configure_reset(custom_config_file: Path):
    content = "Custom config content written here"
    custom_config_file.write_text(content)
    assert custom_config_file.exists()
    assert content in custom_config_file.read_text()

    res = configure(custom_config_file, reset=True)

    assert res == RESULT_FAILURE
    assert custom_config_file.exists()
    assert content not in custom_config_file.read_text()
