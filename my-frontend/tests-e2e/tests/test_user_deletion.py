from playwright.sync_api import Page
from pages.participants_page import ParticipantsPage

# Позитивний сценарій:
# Admin може видалити учасника, і той зникає зі списку.

def test_admin_can_delete_participant(page: Page, base_url: str, room_id: str):
    participants = ParticipantsPage(page, base_url, room_id)

    # GIVEN: адмін на сторінці учасників, користувач u2 є в кімнаті
    participants.open()
    page.wait_for_timeout(5000) # 5 секунд
    participants.expect_participant_present("u2")

    # WHEN: адмін видаляє u2
    participants.delete_participant("u2")

    # THEN: u2 зникає зі списку, і ми бачимо повідомлення про успіх
    participants.expect_participant_not_present("u2")
    participants.expect_success_toast()


# Негативний сценарій:
# Admin не може видалити самого себе (рядок admin без кнопки Remove)

def test_admin_cannot_delete_self(page: Page, base_url: str, room_id: str):
    participants = ParticipantsPage(page, base_url, room_id)

    # GIVEN: сторінка учасників відкрита
    participants.open()

    # WHEN / THEN: у admin немає кнопки Remove
    admin_row = participants.participant_row("u1")
    remove_buttons = admin_row.get_by_role("button", name="Remove")
    # очікуємо, що в цьому рядку немає кнопки Remove
    assert remove_buttons.count() == 0
