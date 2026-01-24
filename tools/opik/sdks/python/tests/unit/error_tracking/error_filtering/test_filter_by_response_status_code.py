from opik.error_tracking.error_filtering import filter_by_response_status_code


def test_filter_by_response_status_code__status_code_from_extra_dict__happyflows(
    real_basic_hint,
    real_error_event_with_status_code_401,
    real_error_event_with_status_code_500,
):
    tested = filter_by_response_status_code.FilterByResponseStatusCode(
        status_codes_to_drop=[401]
    )

    assert (
        tested.process_event(real_error_event_with_status_code_500, real_basic_hint)
        is True
    )

    assert (
        tested.process_event(real_error_event_with_status_code_401, real_basic_hint)
        is False
    )


def test_filter_by_response_status_code__status_code_from_exception_attribute__happyflows(
    real_hint_with_exception_with_status_code_401,
    real_hint_with_exception_with_status_code_500,
    real_error_event,
):
    tested = filter_by_response_status_code.FilterByResponseStatusCode(
        status_codes_to_drop=[401]
    )

    assert (
        tested.process_event(
            real_error_event, real_hint_with_exception_with_status_code_500
        )
        is True
    )

    assert (
        tested.process_event(
            real_error_event, real_hint_with_exception_with_status_code_401
        )
        is False
    )
