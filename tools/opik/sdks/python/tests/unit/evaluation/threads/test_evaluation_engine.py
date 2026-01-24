import unittest
from unittest import mock
from unittest.mock import patch

import pytest

from opik import exceptions
from opik.api_objects.conversation import conversation_thread
from opik.api_objects.threads import threads_client
from opik.evaluation.metrics import score_result
from opik.evaluation.metrics.conversation import conversation_thread_metric
from opik.evaluation.threads import evaluation_engine, evaluation_result
from opik.rest_api import TraceThread


class TestThreadsEvaluationEngine(unittest.TestCase):
    def setUp(self):
        # Mock the threads client
        self.prod_client = mock.MagicMock(spec=threads_client.ThreadsClient)
        self.prod_opik_client = mock.MagicMock()
        self.prod_client.opik_client = self.prod_opik_client

        # Setup the evaluation engine
        self.project_name = "test_project"
        self.engine = evaluation_engine.ThreadsEvaluationEngine(
            client=self.prod_client,
            project_name=self.project_name,
            number_of_workers=2,
            verbose=0,
        )

        # Mock trace and span for testing
        self.prod_trace = mock.MagicMock()
        self.prod_trace.id = "trace_id_123"
        self.prod_span = mock.MagicMock()
        self.prod_span.id = "span_id_456"
        self.prod_opik_client.trace.return_value = self.prod_trace
        self.prod_opik_client.span.return_value = self.prod_span

    def test_evaluate_threads__happy_path(self):
        """Test the full evaluate_threads method with mocked dependencies. Two threads should be evaluated and logged."""
        # Mock threads
        prod_threads = [
            TraceThread(id="thread_1", status="inactive"),
            TraceThread(id="thread_2", status="inactive"),
        ]
        self.prod_client.search_threads.return_value = prod_threads

        # Create mock metrics
        prod_metric1 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric1.name = "metric1"
        prod_metric2 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric2.name = "metric2"
        metrics = [prod_metric1, prod_metric2]

        # Patch the evaluate_thread method
        self.engine.evaluate_thread = _prod_evaluate_thread_two_test_results

        # Call the method
        result = self.engine.evaluate_threads(
            filter_string="test_filter",
            eval_project_name="eval_project",
            metrics=metrics,
            trace_input_transform=lambda x: "",
            trace_output_transform=lambda x: "",
            max_traces_per_thread=10,
        )

        # Verify the result
        self.assertEqual(len(result.results), 2)
        for result in result.results:
            self.assertTrue(result.thread_id in ["thread_1", "thread_2"])
            self.assertEqual(len(result.scores), 2)

        # Verify the log_feedback_scores was called
        self.prod_client.log_threads_feedback_scores.assert_called()

    def test_evaluate_threads__one_thread_closed__happy_path(self):
        """Test the full evaluate_threads method with mocked dependencies for two threads one is closed and one is active.
        Only one feedback score should be logged for the closed thread."""
        # Mock threads
        prod_threads = [
            TraceThread(id="thread_1", status="inactive"),
            TraceThread(id="thread_2", status="active"),
        ]
        self.prod_client.search_threads.return_value = prod_threads

        # Create mock metrics
        prod_metric1 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric1.name = "metric1"
        prod_metric2 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric2.name = "metric2"
        metrics = [prod_metric1, prod_metric2]

        # Patch the evaluate_thread method
        self.engine.evaluate_thread = _prod_evaluate_thread_two_test_results

        filter_string = "test_filter"

        # Call the method
        with self.assertLogs(
            level="WARNING", logger="opik.evaluation.threads.evaluation_engine"
        ) as log_context:
            result = self.engine.evaluate_threads(
                filter_string=filter_string,
                eval_project_name="eval_project",
                metrics=metrics,
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
                max_traces_per_thread=10,
            )

        # Verify the result
        self.assertEqual(len(result.results), 1)
        for result in result.results:
            self.assertTrue(result.thread_id in ["thread_1"])
            self.assertEqual(len(result.scores), 2)

        # Verify the log_feedback_scores was called
        self.prod_client.log_threads_feedback_scores.assert_called()

        active_threads_ids = [
            thread.id for thread in prod_threads if thread.status == "active"
        ]
        inactive_threads_ids = [
            thread.id for thread in prod_threads if thread.status == "inactive"
        ]
        # Verify warning was logged
        self.assertTrue(
            any(
                f"Some threads are active: {active_threads_ids} with filter_string: {filter_string}. Only closed threads will be evaluated: {inactive_threads_ids}."
                in message
                for message in log_context.output
            )
        )

    def test_evaluate_threads__with_empty_traces__warning_logged(self):
        """Test evaluate_threads when no traces are found."""
        # Mock an empty traces list
        self.prod_opik_client.search_traces.return_value = []

        # Mock threads
        prod_threads = [
            TraceThread(id="thread_1", status="inactive"),
        ]
        self.prod_client.search_threads.return_value = prod_threads

        # Create mock metrics
        prod_metric1 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric1.name = "metric1"
        prod_score1 = score_result.ScoreResult(name="metric1", value=0.8, reason="Good")
        prod_metric1.score.return_value = prod_score1

        # Call the method
        with self.assertLogs(
            level="WARNING", logger="opik.evaluation.threads.evaluation_engine"
        ) as log_context:
            results = self.engine.evaluate_threads(
                filter_string="filter_string",
                eval_project_name="eval_project",
                metrics=[prod_metric1],
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
                max_traces_per_thread=10,
            )

        # Verify the result
        self.assertEqual(len(results.results), 1)
        result = results.results[0]

        self.assertEqual(result.thread_id, "thread_1")
        self.assertEqual(len(result.scores), 0)

        # Verify error was logged
        self.assertTrue(
            any(
                f"Thread '{prod_threads[0].id}' has no conversation traces. Skipping evaluation."
                in message
                for message in log_context.output
            )
        )

    def test_evaluate_threads__no_threads_found__exception_raised(self):
        """Test evaluate_threads when no threads are found."""
        # Mock an empty threads list
        self.prod_client.search_threads.return_value = []

        # Create mock metrics
        prod_metric = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        metrics = [prod_metric]

        filter_string = "test_filter"

        # Call the method
        with pytest.raises(exceptions.EvaluationError) as exc_info:
            self.engine.evaluate_threads(
                filter_string="test_filter",
                eval_project_name="eval_project",
                metrics=metrics,
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
            )

        assert (
            str(exc_info.value)
            == f"No threads found with filter_string: {filter_string}"
        )

    def test_evaluate_threads__no_closed_threads_found__exception_raised(self):
        # Mock threads
        prod_threads = [
            TraceThread(id="thread_1", status="active"),
            TraceThread(id="thread_2", status="active"),
        ]
        self.prod_client.search_threads.return_value = prod_threads

        # Create mock metrics
        prod_metric = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        metrics = [prod_metric]

        filter_string = "test_filter"

        # Call the method
        with pytest.raises(exceptions.EvaluationError) as exc_info:
            self.engine.evaluate_threads(
                filter_string=filter_string,
                eval_project_name="eval_project",
                metrics=metrics,
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
            )

        assert (
            str(exc_info.value)
            == f"No closed threads found with filter_string: {filter_string}. Only closed threads can be evaluated."
        )

    def test_evaluate_threads__with_multiple_trace_threads__executor_called_with_correct_args(
        self,
    ):
        """Test evaluate_threads with multiple trace threads and multiple workers.
        Verify the executor was called with the right number of workers and tasks."""

        # Create an engine with multiple workers
        engine = evaluation_engine.ThreadsEvaluationEngine(
            client=self.prod_client,
            project_name=self.project_name,
            number_of_workers=4,  # Use multiple workers
            verbose=1,
        )

        # Mock threads - create several to test concurrency
        prod_threads = [
            TraceThread(id=f"thread_{i}", status="inactive")
            for i in range(10)  # Create 10 threads
        ]
        self.prod_client.search_threads.return_value = prod_threads

        # Mock the evaluation executor
        with mock.patch(
            "opik.evaluation.threads.evaluation_engine.evaluation_tasks_executor.execute"
        ) as prod_execute:
            # Create a mock result
            results = [
                evaluation_result.ThreadEvaluationResult(
                    thread_id=f"thread_{i}",
                    scores=[
                        score_result.ScoreResult(
                            name="metric", value=0.8, reason="Good"
                        ),
                    ],
                )
                for i in range(10)
            ]
            prod_execute.return_value = results

            # Create mock metric
            prod_metric = mock.MagicMock(
                spec=conversation_thread_metric.ConversationThreadMetric
            )
            metrics = [prod_metric]

            # Call the method
            engine.evaluate_threads(
                filter_string=None,
                eval_project_name="eval_project",
                metrics=metrics,
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
            )

            # Verify the number of tasks matches the number of threads
            self.assertEqual(len(prod_execute.call_args[0][0]), 10)

            # Verify the executor was called with the right number of workers and verbose value
            prod_execute.assert_called_once()
            self.assertEqual(prod_execute.call_args[1]["workers"], 4)
            self.assertEqual(prod_execute.call_args[1]["verbose"], 1)

    def test_evaluate_threads__with_no_metrics__raises_exception(self):
        """Test _evaluate_thread when no metrics are provided."""
        with pytest.raises(ValueError):
            # Call the method with an empty metrics list
            self.engine.evaluate_threads(
                filter_string="filter_string",
                eval_project_name="eval_project",
                metrics=[],  # Empty metrics list
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
                max_traces_per_thread=10,
            )

    @patch("opik.decorator.base_track_decorator.opik_client")
    @patch("opik.evaluation.threads.evaluation_engine.helpers.load_conversation_thread")
    def test_evaluate_thread(self, load_conversation_thread, decorator_opik_client):
        """Test that evaluate_thread correctly evaluates a thread with metrics."""
        mocked_opik_client = mock.MagicMock()
        decorator_opik_client.get_client_cached.return_value = mocked_opik_client

        # Create a mock conversation thread
        prod_conversation = conversation_thread.ConversationThread()
        prod_conversation.add_user_message("Hello")
        prod_conversation.add_assistant_message("Hi there")

        # Mock the load_conversation_thread method
        load_conversation_thread.return_value = prod_conversation

        # Create mock metrics
        prod_metric1 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric1.name = "metric1"
        prod_score1 = score_result.ScoreResult(name="metric1", value=0.8, reason="Good")
        prod_metric1.score.return_value = prod_score1

        prod_metric2 = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_metric2.name = "metric2"
        prod_score2 = score_result.ScoreResult(
            name="metric2", value=0.6, reason="Average"
        )
        prod_metric2.score.return_value = [prod_score2]  # Test list return

        metrics = [prod_metric1, prod_metric2]

        # Call the method
        result = self.engine.evaluate_thread(
            thread=TraceThread(id="thread_1"),
            eval_project_name="eval_project",
            metrics=metrics,
            trace_input_transform=lambda x: "",
            trace_output_transform=lambda x: "",
            max_traces_per_thread=10,
        )

        # Verify the result
        self.assertEqual(result.thread_id, "thread_1")
        self.assertEqual(len(result.scores), 2)
        self.assertEqual(result.scores[0].name, "metric1")
        self.assertEqual(result.scores[0].value, 0.8)
        self.assertEqual(result.scores[1].name, "metric2")
        self.assertEqual(result.scores[1].value, 0.6)

        # Verify the trace and span calls
        self.prod_opik_client.trace.assert_called()
        mocked_opik_client.span.assert_called()

        # Verify metrics were called with the right parameters
        conversation_list = prod_conversation.model_dump()["discussion"]
        prod_metric1.score.assert_called_once_with(conversation_list)
        prod_metric2.score.assert_called_once_with(conversation_list)

    @patch("opik.decorator.base_track_decorator.opik_client")
    @patch("opik.evaluation.threads.evaluation_engine.helpers.load_conversation_thread")
    def test_evaluate_thread__error_in_metric_logged(
        self, load_conversation_thread, decorator_opik_client
    ):
        """Test that evaluate_thread logs errors in metrics."""
        mocked_opik_client = mock.MagicMock()
        decorator_opik_client.get_client_cached.return_value = mocked_opik_client

        # Create a mock thread
        thread = TraceThread(id="thread_1")

        # Create a mock conversation thread
        prod_conversation = conversation_thread.ConversationThread()
        prod_conversation.add_user_message("Hello")
        prod_conversation.add_assistant_message("Hi there")

        # Mock the load_conversation_thread method
        load_conversation_thread.return_value = prod_conversation

        # Create a metric that raises an exception
        prod_error_metric = mock.MagicMock(
            spec=conversation_thread_metric.ConversationThreadMetric
        )
        prod_error_metric.name = "error_metric"
        prod_error_metric.score.side_effect = ValueError("Test error in metric")

        metrics = [prod_error_metric]

        # Call the method and expect it to handle the error
        with self.assertLogs(
            level="ERROR", logger="opik.evaluation.threads.evaluation_engine"
        ) as log_context:
            self.engine.evaluate_thread(
                thread=thread,
                eval_project_name="eval_project",
                metrics=metrics,
                trace_input_transform=lambda x: "",
                trace_output_transform=lambda x: "",
                max_traces_per_thread=10,
            )

            # Verify error was logged
            self.assertTrue(
                any(
                    f"Failed to compute metric {prod_error_metric.name}. Score result will be marked as failed."
                    in message
                    for message in log_context.output
                )
            )


def _prod_evaluate_thread_two_test_results(*args, **kwargs):
    # Mock evaluate_thread to return two test results
    thread = kwargs.get("thread")
    return evaluation_result.ThreadEvaluationResult(
        thread_id=thread.id,
        scores=[
            score_result.ScoreResult(name="metric1", value=0.8, reason="Good"),
            score_result.ScoreResult(name="metric2", value=0.6, reason="Average"),
        ],
    )
