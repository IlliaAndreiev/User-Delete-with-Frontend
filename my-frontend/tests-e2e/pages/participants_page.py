from playwright.sync_api import Page, expect

class ParticipantsPage:
    def __init__(self, page: Page, base_url: str, room_id: str = "r1"):
        self.page = page
        self.base_url = base_url
        self.room_id = room_id

    # ====== Навігація ======
    def open(self):
        self.page.goto(f"{self.base_url}/")
        expect(self.page.get_by_text("Who’s Playing?")).to_be_visible()

    # ====== Локатори ======
    def participant_row(self, name: str):
        return self.page.get_by_role("listitem").filter(has_text=name)

    def remove_button_for(self, name: str):
        row = self.participant_row(name)
        return row.get_by_role("button", name="Remove")

    def confirm_modal(self):
        return self.page.get_by_role("dialog", name="Remove participant?")

    def confirm_button(self):
        return self.page.get_by_role("button", name="Remove")

    def cancel_button(self):
        return self.page.get_by_role("button", name="Cancel")

    def toast(self):
        return self.page.get_by_text("Учасника видалено.")

    # ====== Дії ======
    def delete_participant(self, name: str):
        # Given: користувач є у списку
        expect(self.participant_row(name)).to_be_visible()

        # When: клікаємо Remove
        self.remove_button_for(name).click()

        # відкрилася модалка
        expect(self.confirm_modal()).to_be_visible()

        # підтверджуємо
        self.confirm_button().click()

    # ====== Перевірки ======
    def expect_participant_present(self, name: str):
        expect(self.participant_row(name)).to_be_visible()

    def expect_participant_not_present(self, name: str):
        expect(self.participant_row(name)).to_have_count(0)

    def expect_success_toast(self):
        expect(self.toast()).to_be_visible()
