import nwb2bids


def test_notification_initialization() -> None:
    for identifier in nwb2bids.notifications.notification_definitions:
        notification = nwb2bids.notifications.Notification.from_definition(identifier=identifier)
        assert notification.identifier == identifier
