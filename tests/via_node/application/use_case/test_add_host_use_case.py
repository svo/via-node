from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that

from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.domain.model.host import Host


class TestAddHostUseCase:
    def test_execute_creates_host_with_correct_ip(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        result = use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
        )

        assert_that(result.ip_address).is_equal_to("192.168.1.1")

    def test_execute_creates_host_with_correct_hostname(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        result = use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
        )

        assert_that(result.hostname).is_equal_to("example.com")

    def test_execute_calls_repository(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
        )

        repository.create_or_update_host.assert_called_once()

    def test_execute_with_metadata(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        metadata = {"version": "1.0", "env": "prod"}
        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        result = use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata=metadata,
        )

        assert_that(result.metadata).is_equal_to(metadata)

    def test_execute_with_invalid_ip_raises_error(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        with pytest.raises(ValueError):
            use_case.execute(
                ip_address="invalid-ip",
                hostname="example.com",
                os_type="Linux",
            )

    def test_execute_sets_created_at_timestamp(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
        )

        call_args = repository.create_or_update_host.call_args
        created_host = call_args[0][0]
        assert_that(created_host.created_at).is_not_none()

    def test_execute_sets_updated_at_timestamp(self) -> None:
        repository = MagicMock()
        use_case = AddHostUseCase(repository)

        expected_host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        repository.create_or_update_host.return_value = expected_host

        use_case.execute(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
        )

        call_args = repository.create_or_update_host.call_args
        created_host = call_args[0][0]
        assert_that(created_host.updated_at).is_not_none()
