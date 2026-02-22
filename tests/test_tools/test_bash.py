from cc_hooks.tools import BashInput


def test_bash_input_alias() -> None:
    model = BashInput(command="ls", runInBackground=True)
    dumped = model.model_dump(by_alias=True, exclude_none=True)
    assert dumped["runInBackground"] is True
