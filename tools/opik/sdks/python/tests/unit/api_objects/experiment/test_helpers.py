import types

import pytest

from opik.api_objects import experiment
from tests.conftest import random_chars


def real_prompt(with_postfix: bool = False):
    postfix = random_chars()

    def __internal_api__to_info_dict__():
        return {
            "name": real_prompt_obj.name,
            "version": {
                "template": real_prompt_obj.prompt,
            },
        }

    real_prompt_obj = types.SimpleNamespace(
        __internal_api__version_id__="some-prompt-version-id",
        prompt="some-prompt-value",
        name="some-prompt-name",
        __internal_api__to_info_dict__=__internal_api__to_info_dict__,
    )

    if with_postfix:
        real_prompt_obj.prompt += postfix
        real_prompt_obj.__internal_api__version_id__ += postfix
        real_prompt_obj.name += postfix

    return real_prompt_obj


@pytest.mark.parametrize(
    argnames="input_kwargs,expected",
    argvalues=[
        (
            {"experiment_config": None, "prompts": None},
            {"metadata": None, "prompt_versions": None},
        ),
        (
            {"experiment_config": {}, "prompts": None},
            {"metadata": None, "prompt_versions": None},
        ),
        (
            {"experiment_config": None, "prompts": [real_prompt()]},
            {
                "metadata": {"prompts": {"some-prompt-name": "some-prompt-value"}},
                "prompt_versions": [{"id": "some-prompt-version-id"}],
            },
        ),
        (
            {"experiment_config": {}, "prompts": [real_prompt()]},
            {
                "metadata": {"prompts": {"some-prompt-name": "some-prompt-value"}},
                "prompt_versions": [{"id": "some-prompt-version-id"}],
            },
        ),
        (
            {"experiment_config": {"some-key": "some-value"}, "prompts": None},
            {"metadata": {"some-key": "some-value"}, "prompt_versions": None},
        ),
        (
            {
                "experiment_config": "NOT-DICT-VALUE-THAT-WILL-BE-IGNORED-AND-REPLACED-WITH-DICT-WITH-PROMPT",
                "prompts": [real_prompt()],
            },
            {
                "metadata": {"prompts": {"some-prompt-name": "some-prompt-value"}},
                "prompt_versions": [{"id": "some-prompt-version-id"}],
            },
        ),
    ],
)
def test_experiment_build_metadata_from_prompt_versions(input_kwargs, expected):
    metadata, prompt_versions = experiment.build_metadata_and_prompt_versions(
        **input_kwargs
    )

    assert metadata == expected["metadata"]
    assert prompt_versions == expected["prompt_versions"]


def test_check_prompt_args_with_none_arguments():
    result = experiment.handle_prompt_args(prompt=None, prompts=None)
    assert result is None


def test_check_prompt_args_with_none_and_empty_list():
    result = experiment.handle_prompt_args(prompt=None, prompts=[])
    assert result is None


def test_check_prompt_args_with_single_prompt():
    prod_prompt = real_prompt(with_postfix=True)
    result = experiment.handle_prompt_args(prompt=prod_prompt, prompts=None)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == prod_prompt


def test_check_prompt_args_with_prompts_list():
    prod_prompt_1 = real_prompt(with_postfix=True)
    prod_prompt_2 = real_prompt(with_postfix=True)
    prompts = [prod_prompt_1, prod_prompt_2]
    result = experiment.handle_prompt_args(prompt=None, prompts=prompts)
    assert result == prompts


def test_check_prompt_args_with_both_prompt_and_prompts():
    prod_prompt = real_prompt(with_postfix=True)
    prod_prompt_list = [
        real_prompt(with_postfix=True),
        real_prompt(with_postfix=True),
    ]
    result = experiment.handle_prompt_args(prompt=prod_prompt, prompts=prod_prompt_list)
    assert isinstance(result, list)
    assert result == prod_prompt_list
