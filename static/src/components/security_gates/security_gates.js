/** @odoo-module */

import { registry } from "@web/core/registry"
import { Component, useState, useRef, onMounted, onWillUnmount, xml } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { renderToElement } from "@web/core/utils/render";

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { SdContactsDashboard } from "../web/employee_contacts_web";

export class SdContactsSecurityGates extends Component {
    static template = "sd_contacts.security_gates_template";
    static components = {SdContactsDashboard };
    setup(){
        console.log('security_gates')
        this.orm = useService('orm')
        this.employeeAttendanceData = useRef('employee_attendance_data')
        this.onEmployeeListClick = this.onEmployeeListClick.bind(this)
    }
    async onEmployeeListClick(e){
    let employee_id = 0;
        if (e.target.classList.contains('employee_image_id')){
            employee_id = e.target.id
        }else if (e.target.parentElement.classList.contains('employee_image_id')){
            employee_id = e.target.parentElement.id
        }
        if(employee_id){
            let data = await this.orm.call('hr.attendance', 'get_attendance', [false, employee_id])
            data = JSON.parse(data)
            console.log('onEmployeeListClick:',employee_id,data )
            const bannerElement = renderToElement("sd_contacts.attendance_template", {
                props: { data },
            });
            this.employeeAttendanceData.el.innerHTML = ''
            this.employeeAttendanceData.el.appendChild(bannerElement)
        }

    }

}

registry.category("actions").add("sd_contacts.security_gates", SdContactsSecurityGates);
