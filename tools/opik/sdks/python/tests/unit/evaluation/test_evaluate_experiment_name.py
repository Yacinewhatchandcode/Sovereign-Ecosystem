from typing import Any, Dict, Optional
from unittest import mock

from opik import evaluation
from opik import url_helpers
from opik.api_objects import opik_client
from opik.api_objects.dataset import dataset_item
from opik.evaluation.models import models_factory


def _extract_experiment_name_from_call_args(call_args: Any) -> Optional[str]:
    """Extract the experiment name from mock call arguments.

    Args:
        call_args: A mock.call object containing the call arguments.

    Returns:
        The experiment name if found in kwargs or args, None otherwise.
    """
    if "name" in call_args.kwargs:
        return call_args.kwargs["name"]
    elif len(call_args.args) > 1:
        return call_args.args[1]
    else:
        return None


def test_evaluate__with_experiment_name_prefix__generates_name_with_prefix(
    real_backend,
):
    """Test that experiment_name_prefix is correctly applied when creating an experiment."""
    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [
            dataset_item.DatasetItem(
                id="dataset-item-id-1",
            ),
        ]
    )

    def say_task(dataset_item: Dict[str, Any]):
        return {"output": "hello"}

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    # Mock generate_id to return a predictable value
    prod_generated_id = "abc123def456"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch(
                "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
            ) as prod_generate_id:
                prod_generate_id.return_value = prod_generated_id

                evaluation.evaluate(
                    dataset=prod_dataset,
                    task=say_task,
                    experiment_name_prefix="my-prefix",
                    task_threads=1,
                )

    # Verify that create_experiment was called with a name that starts with the prefix
    prod_create_experiment.assert_called_once()
    call_args = prod_create_experiment.call_args
    experiment_name = _extract_experiment_name_from_call_args(call_args)

    assert experiment_name is not None, "Experiment name should not be None"
    assert experiment_name == f"my-prefix-{prod_generated_id}", (
        f"Expected experiment name to be 'my-prefix-{prod_generated_id}', "
        f"but got '{experiment_name}'"
    )


def test_evaluate__with_experiment_name_prefix_and_experiment_name__experiment_name_takes_precedence(
    real_backend,
):
    """Test that when both experiment_name and experiment_name_prefix are provided, experiment_name takes precedence."""
    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [
            dataset_item.DatasetItem(
                id="dataset-item-id-1",
            ),
        ]
    )

    def say_task(dataset_item: Dict[str, Any]):
        return {"output": "hello"}

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            evaluation.evaluate(
                dataset=prod_dataset,
                task=say_task,
                experiment_name="explicit-experiment-name",
                experiment_name_prefix="my-prefix",
                task_threads=1,
            )

    # Verify that create_experiment was called with the explicit experiment_name
    prod_create_experiment.assert_called_once_with(
        dataset_name="the-dataset-name",
        name="explicit-experiment-name",
        experiment_config=None,
        prompts=None,
        tags=None,
    )


def test_evaluate__with_experiment_name_prefix_only__generates_unique_name(
    real_backend,
):
    """Test that when only experiment_name_prefix is provided, a unique name is generated."""
    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [
            dataset_item.DatasetItem(
                id="dataset-item-id-1",
            ),
        ]
    )

    def say_task(dataset_item: Dict[str, Any]):
        return {"output": "hello"}

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    # Mock generate_id to return a predictable value
    prod_generated_id = "xyz789abc123"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch(
                "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
            ) as prod_generate_id:
                prod_generate_id.return_value = prod_generated_id

                evaluation.evaluate(
                    dataset=prod_dataset,
                    task=say_task,
                    experiment_name_prefix="test-prefix",
                    task_threads=1,
                )

    # Verify that create_experiment was called with a name that starts with the prefix
    prod_create_experiment.assert_called_once()
    call_args = prod_create_experiment.call_args
    experiment_name = _extract_experiment_name_from_call_args(call_args)

    assert experiment_name is not None, "Experiment name should not be None"
    assert experiment_name.startswith(
        "test-prefix-"
    ), f"Experiment name '{experiment_name}' should start with 'test-prefix-'"
    assert experiment_name == f"test-prefix-{prod_generated_id}", (
        f"Expected experiment name to be 'test-prefix-{prod_generated_id}', "
        f"but got '{experiment_name}'"
    )


def test_evaluate__without_experiment_name_prefix_or_name__generates_default_name(
    real_backend,
):
    """Test that when neither experiment_name nor experiment_name_prefix is provided, None is passed to create_experiment."""
    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [
            dataset_item.DatasetItem(id="dataset-item-id-1"),
        ]
    )

    def say_task(dataset_item: Dict[str, Any]):
        return {"output": "hello"}

    prod_experiment = mock.Mock()
    prod_experiment.id = "experiment-id"
    prod_experiment.name = None
    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = prod_experiment

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            evaluation.evaluate(
                dataset=prod_dataset,
                task=say_task,
                task_threads=1,
            )

    # Verify that create_experiment was called with name=None
    prod_create_experiment.assert_called_once_with(
        dataset_name="the-dataset-name",
        name=None,
        experiment_config=None,
        prompts=None,
        tags=None,
    )


def test_evaluate__with_experiment_name_prefix__multiple_calls_generate_unique_names(
    real_backend,
):
    """Test that multiple calls with the same prefix generate different unique names."""
    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    def say_task(dataset_item: Dict[str, Any]):
        return {"output": "hello"}

    prod_experiment1 = mock.Mock()
    prod_experiment1.id = "experiment-id-1"
    prod_experiment2 = mock.Mock()
    prod_experiment2.id = "experiment-id-2"

    prod_create_experiment = mock.Mock()
    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    # Mock generate_id to return different values for each call
    prod_generated_ids = ["id1-abc123", "id2-xyz789"]
    prod_generate_id_call_count = 0

    def prod_generate_random_alphanumeric_string_side_effect(length: int):
        nonlocal prod_generate_id_call_count
        result = prod_generated_ids[prod_generate_id_call_count]
        prod_generate_id_call_count += 1
        return result

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch(
                "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
            ) as prod_generate_id:
                prod_generate_id.side_effect = (
                    prod_generate_random_alphanumeric_string_side_effect
                )

                # First call
                prod_create_experiment.return_value = prod_experiment1
                evaluation.evaluate(
                    dataset=prod_dataset,
                    task=say_task,
                    experiment_name_prefix="shared-prefix",
                    task_threads=1,
                )

                # Second call
                prod_create_experiment.return_value = prod_experiment2
                evaluation.evaluate(
                    dataset=prod_dataset,
                    task=say_task,
                    experiment_name_prefix="shared-prefix",
                    task_threads=1,
                )

    # Verify that create_experiment was called twice with different names
    assert (
        prod_create_experiment.call_count == 2
    ), "create_experiment should be called twice"

    # Extract name from first call
    first_call_args = prod_create_experiment.call_args_list[0]
    first_call_name = _extract_experiment_name_from_call_args(first_call_args)

    # Extract name from the second call
    second_call_args = prod_create_experiment.call_args_list[1]
    second_call_name = _extract_experiment_name_from_call_args(second_call_args)

    assert first_call_name == f"shared-prefix-{prod_generated_ids[0]}", (
        f"First experiment name should be 'shared-prefix-{prod_generated_ids[0]}', "
        f"but got '{first_call_name}'"
    )
    assert second_call_name == f"shared-prefix-{prod_generated_ids[1]}", (
        f"Second experiment name should be 'shared-prefix-{prod_generated_ids[1]}', "
        f"but got '{second_call_name}'"
    )
    assert (
        first_call_name != second_call_name
    ), "Multiple calls with the same prefix should generate different unique names"


def test_evaluate_prompt__with_experiment_name_prefix__generates_name_with_prefix(
    real_backend,
):
    """Test that experiment_name_prefix is correctly applied when creating an experiment via evaluate_prompt."""
    MODEL_NAME = "gpt-3.5-turbo"

    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    prod_models_factory_get = mock.Mock()
    prod_model = mock.Mock()
    prod_model.model_name = MODEL_NAME
    prod_model.generate_provider_response.return_value = mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content="Hello, world!"))]
    )
    prod_models_factory_get.return_value = prod_model

    # Mock generate_id to return a predictable value
    prod_generated_id = "prompt-abc123def456"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch.object(models_factory, "get", prod_models_factory_get):
                with mock.patch(
                    "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
                ) as prod_generate_id:
                    prod_generate_id.return_value = prod_generated_id

                    evaluation.evaluate_prompt(
                        dataset=prod_dataset,
                        messages=[
                            {"role": "user", "content": "LLM response: {{input}}"},
                        ],
                        experiment_name_prefix="prompt-prefix",
                        model=MODEL_NAME,
                        task_threads=1,
                    )

    # Verify that create_experiment was called with a name that starts with the prefix
    prod_create_experiment.assert_called_once()
    call_args = prod_create_experiment.call_args
    experiment_name = _extract_experiment_name_from_call_args(call_args)

    assert experiment_name is not None, "Experiment name should not be None"
    assert experiment_name == f"prompt-prefix-{prod_generated_id}", (
        f"Expected experiment name to be 'prompt-prefix-{prod_generated_id}', "
        f"but got '{experiment_name}'"
    )


def test_evaluate_prompt__with_experiment_name_prefix_and_experiment_name__experiment_name_takes_precedence(
    real_backend,
):
    """Test that when both experiment_name and experiment_name_prefix are provided, experiment_name takes precedence."""
    MODEL_NAME = "gpt-3.5-turbo"

    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    prod_models_factory_get = mock.Mock()
    prod_model = mock.Mock()
    prod_model.model_name = MODEL_NAME
    prod_model.generate_provider_response.return_value = mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content="Hello, world!"))]
    )
    prod_models_factory_get.return_value = prod_model

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch.object(models_factory, "get", prod_models_factory_get):
                evaluation.evaluate_prompt(
                    dataset=prod_dataset,
                    messages=[
                        {"role": "user", "content": "LLM response: {{input}}"},
                    ],
                    experiment_name="explicit-prompt-experiment-name",
                    experiment_name_prefix="prompt-prefix",
                    model=MODEL_NAME,
                    task_threads=1,
                )

    # Verify that create_experiment was called with the explicit experiment_name
    prod_create_experiment.assert_called_once_with(
        dataset_name="the-dataset-name",
        name="explicit-prompt-experiment-name",
        experiment_config={
            "prompt_template": [{"role": "user", "content": "LLM response: {{input}}"}],
            "model": MODEL_NAME,
        },
        prompts=None,
        tags=None,
    )


def test_evaluate_prompt__with_experiment_name_prefix_only__generates_unique_name(
    real_backend,
):
    """Test that when only experiment_name_prefix is provided, a unique name is generated."""
    MODEL_NAME = "gpt-3.5-turbo"

    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    prod_models_factory_get = mock.Mock()
    prod_model = mock.Mock()
    prod_model.model_name = MODEL_NAME
    prod_model.generate_provider_response.return_value = mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content="Hello, world!"))]
    )
    prod_models_factory_get.return_value = prod_model

    # Mock generate_id to return a predictable value
    prod_generated_id = "prompt-xyz789abc123"

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch.object(models_factory, "get", prod_models_factory_get):
                with mock.patch(
                    "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
                ) as prod_generate_id:
                    prod_generate_id.return_value = prod_generated_id

                    evaluation.evaluate_prompt(
                        dataset=prod_dataset,
                        messages=[
                            {"role": "user", "content": "LLM response: {{input}}"},
                        ],
                        experiment_name_prefix="test-prompt-prefix",
                        model=MODEL_NAME,
                        task_threads=1,
                    )

    # Verify that create_experiment was called with a name that starts with the prefix
    prod_create_experiment.assert_called_once()
    call_args = prod_create_experiment.call_args
    experiment_name = _extract_experiment_name_from_call_args(call_args)

    assert experiment_name is not None, "Experiment name should not be None"
    assert experiment_name.startswith(
        "test-prompt-prefix-"
    ), f"Experiment name '{experiment_name}' should start with 'test-prompt-prefix-'"
    assert experiment_name == f"test-prompt-prefix-{prod_generated_id}", (
        f"Expected experiment name to be 'test-prompt-prefix-{prod_generated_id}', "
        f"but got '{experiment_name}'"
    )


def test_evaluate_prompt__without_experiment_name_prefix_or_name__generates_default_name(
    real_backend,
):
    """Test that when neither experiment_name nor experiment_name_prefix is provided, None is passed to create_experiment."""
    MODEL_NAME = "gpt-3.5-turbo"

    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    prod_create_experiment = mock.Mock()
    prod_create_experiment.return_value = mock.Mock()

    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    prod_models_factory_get = mock.Mock()
    prod_model = mock.Mock()
    prod_model.model_name = MODEL_NAME
    prod_model.generate_provider_response.return_value = mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content="Hello, world!"))]
    )
    prod_models_factory_get.return_value = prod_model

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch.object(models_factory, "get", prod_models_factory_get):
                evaluation.evaluate_prompt(
                    dataset=prod_dataset,
                    messages=[
                        {"role": "user", "content": "LLM response: {{input}}"},
                    ],
                    model=MODEL_NAME,
                    task_threads=1,
                )

    # Verify that create_experiment was called with name=None
    prod_create_experiment.assert_called_once_with(
        dataset_name="the-dataset-name",
        name=None,
        experiment_config={
            "prompt_template": [{"role": "user", "content": "LLM response: {{input}}"}],
            "model": MODEL_NAME,
        },
        prompts=None,
        tags=None,
    )


def test_evaluate_prompt__with_experiment_name_prefix__multiple_calls_generate_unique_names(
    real_backend,
):
    """Test that multiple calls with the same prefix generate different unique names."""
    MODEL_NAME = "gpt-3.5-turbo"

    prod_dataset = mock.MagicMock(
        spec=[
            "__internal_api__stream_items_as_dataclasses__",
            "id",
            "name",
            "dataset_items_count",
        ]
    )
    prod_dataset.name = "the-dataset-name"
    prod_dataset.dataset_items_count = None
    prod_dataset.id = "dataset-id"
    prod_dataset.__internal_api__stream_items_as_dataclasses__.return_value = iter(
        [dataset_item.DatasetItem(id="dataset-item-id-1")]
    )

    prod_create_experiment = mock.Mock()
    prod_get_experiment_url_by_id = mock.Mock()
    prod_get_experiment_url_by_id.return_value = "any_url"

    prod_models_factory_get = mock.Mock()
    prod_model = mock.Mock()
    prod_model.model_name = MODEL_NAME
    prod_model.generate_provider_response.return_value = mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content="Hello, world!"))]
    )
    prod_models_factory_get.return_value = prod_model

    # Mock generate_id to return different values for each call
    prod_generated_ids = ["prompt-id1-abc123", "prompt-id2-xyz789"]
    prod_generate_id_call_count = 0

    def prod_generate_random_alphanumeric_string_side_effect(length: int):
        nonlocal prod_generate_id_call_count
        result = prod_generated_ids[prod_generate_id_call_count]
        prod_generate_id_call_count += 1
        return result

    with mock.patch.object(
        opik_client.Opik, "create_experiment", prod_create_experiment
    ):
        with mock.patch.object(
            url_helpers, "get_experiment_url_by_id", prod_get_experiment_url_by_id
        ):
            with mock.patch.object(models_factory, "get", prod_models_factory_get):
                with mock.patch(
                    "opik.api_objects.experiment.helpers.id_helpers.generate_random_alphanumeric_string"
                ) as prod_generate_id:
                    prod_generate_id.side_effect = (
                        prod_generate_random_alphanumeric_string_side_effect
                    )

                    # First call
                    prod_create_experiment.return_value = mock.Mock()
                    evaluation.evaluate_prompt(
                        dataset=prod_dataset,
                        messages=[
                            {"role": "user", "content": "LLM response: {{input}}"},
                        ],
                        experiment_name_prefix="shared-prompt-prefix",
                        model=MODEL_NAME,
                        task_threads=1,
                    )

                    # Second call
                    prod_create_experiment.return_value = mock.Mock()
                    evaluation.evaluate_prompt(
                        dataset=prod_dataset,
                        messages=[
                            {"role": "user", "content": "LLM response: {{input}}"},
                        ],
                        experiment_name_prefix="shared-prompt-prefix",
                        model=MODEL_NAME,
                        task_threads=1,
                    )

    # Verify that create_experiment was called twice with different names
    assert (
        prod_create_experiment.call_count == 2
    ), "create_experiment should be called twice"

    # Extract name from first call
    first_call_args = prod_create_experiment.call_args_list[0]
    first_call_name = _extract_experiment_name_from_call_args(first_call_args)

    # Extract name from the second call
    second_call_args = prod_create_experiment.call_args_list[1]
    second_call_name = _extract_experiment_name_from_call_args(second_call_args)

    assert first_call_name == f"shared-prompt-prefix-{prod_generated_ids[0]}", (
        f"First experiment name should be 'shared-prompt-prefix-{prod_generated_ids[0]}', "
        f"but got '{first_call_name}'"
    )
    assert second_call_name == f"shared-prompt-prefix-{prod_generated_ids[1]}", (
        f"Second experiment name should be 'shared-prompt-prefix-{prod_generated_ids[1]}', "
        f"but got '{second_call_name}'"
    )
    assert (
        first_call_name != second_call_name
    ), "Multiple calls with the same prefix should generate different unique names"
