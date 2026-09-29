import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

export const deleteAnythingHotkeyService = {
    dependencies: ["hotkey", "action"],
    start(env, { hotkey: hotkeyService, action: actionService }) {
        // Đăng ký phím tắt toàn cục Ctrl + D
        hotkeyService.add("control+d", () => {
            if (!user.isAdmin) {
                return;
            }
            actionService.doAction("delete_anything.action_delete_anything_wizard");
        }, {
            bypassEditableProtection: true,
            global: true,
        });
    },
};

// Đăng ký service vào hệ thống Web Client
registry.category("services").add("delete_anything_hotkey", deleteAnythingHotkeyService);
