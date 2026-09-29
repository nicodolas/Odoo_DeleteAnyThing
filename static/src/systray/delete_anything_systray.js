import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

export class DeleteAnythingSystray extends Component {
    static template = "delete_anything.Systray";
    static props = {};

    setup() {
        this.actionService = useService("action");
    }

    openWizard() {
        this.actionService.doAction("delete_anything.action_delete_anything_wizard");
    }
}

export const deleteAnythingSystrayItem = {
    Component: DeleteAnythingSystray,
    isDisplayed: () => user.isAdmin,
};

// Đăng ký vào Systray với sequence 99 (đặt ngay bên cạnh Debug mode menu có sequence 100)
registry.category("systray").add("delete_anything.systray", deleteAnythingSystrayItem, { sequence: 99 });
