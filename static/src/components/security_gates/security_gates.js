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
        let self = this;
        console.log('security_gates')
        this.orm = useService('orm')
        this.action = useService("action");
        this.state = useState({
            sendUpdates: 1,
        })

        this.employeeAttendanceData = useRef('employee_attendance_data')
        this.SdContactsDashboardRef = useRef('sd_contacts_dashboard')
        this.lastAttendanceListViewRef = useRef('last_attendance_list_view')
        this.onEmployeeListClick = this.onEmployeeListClick.bind(this)
        this.onInOutClick = this.onInOutClick.bind(this)
        this.onCounterClick = this.onCounterClick.bind(this)
        this.lastAttendanceListViewUpdate = this.lastAttendanceListViewUpdate.bind(this)
        onMounted(async () => {
            self.lastAttendanceListViewUpdate()
        })
        console.log('SEC:', this)

    }
    async onEmployeeListClick(e, employee_id=0){
        console.log('onEmployeeListClick 1:',employee_id )

        if (employee_id == 0 && e.target.classList.contains('employee_image_id')){
            employee_id = e.target.id
        }else if (employee_id == 0 && e.target.parentElement.classList.contains('employee_image_id')){
            employee_id = e.target.parentElement.id
        }
        if(employee_id){
            let data = await this.orm.call('hr.attendance', 'get_attendance', [false, employee_id])
            data = JSON.parse(data)
            console.log('onEmployeeListClick 2:',employee_id,data )
            const bannerElement = renderToElement("sd_contacts.attendance_template", {
                props: { data, }, this: this
            });
            this.employeeAttendanceData.el.innerHTML = ''
            this.employeeAttendanceData.el.appendChild(bannerElement)

        }
        this.updatePresenceState()
        this.lastAttendanceListViewUpdate()


    }
    onCounterClick(e){
        console.log('onCounterClick:\n', e)
        let res_model, domain, context, action_name;
        if(e == 'presents'){
            action_name = _t("Action List")
//            domain.push(['state', 'not in', ['stop_card', 'dismiss']])
//            console.log('domain:', domain)
            res_model = "hr.attendance"
            context = {search_default_present: 1}
        } else {
            return
        }
        this.action.doAction(
            {
                type: "ir.actions.act_window",
                name: action_name,
                res_model: res_model,
                views: [[false, "list"],],
                view_mode: "list",
                target: "current",
//                res_id: res_id,
//                domain: domain,
                context: context,

            })
    }
    async onInOutClick(employee_id){
        let data = await this.orm.call('hr.attendance', 'set_attendance', [false, employee_id])
        this.onEmployeeListClick(false, employee_id)
        this.state.sendUpdates = [{id: 4, hr_icon_display: this.state.sendUpdates.hr_icon_display == 'presence_present' ? 'presence_absence' : 'presence_present'}]
    }
    sendUpdates(){
        console.log('sendUpdates')
    }
    updatePresenceState(){
        let imageStatus = document.querySelectorAll('div.img_div.employee_image_id')
//       console.log(imageStatus)
       //todo: if employee is present, add border-success class

//        let employees = await this.orm.call('hr.employees', 'get_attendance', [false, employee_id])

    }
    async lastAttendanceListViewUpdate(){
//                let lastAttendances = await this.orm.searchRead('hr.attendance', [], ['id', 'employee_id', 'check_in', 'check_out'], {limit: 10, order: 'write_date desc'})
//                console.log('lastAttendances 1', )
                let lastAttendancesData = await this.orm.call('hr.attendance', 'get_last_attendances', [false, 12] )
                lastAttendancesData = JSON.parse(lastAttendancesData)
                const lastAttendances = lastAttendancesData.last_attendances_time
                const presents = lastAttendancesData.presents
                const absence = lastAttendancesData.absence
                const today = lastAttendancesData.today

//                console.log('lastAttendances 2', lastAttendances)
            const lastAttendanceElement = renderToElement("sd_contacts.last_attendance_template", {
                props: { lastAttendances, presents, absence, today }, this: this
            });
            this.lastAttendanceListViewRef.el.innerHTML = ''
            this.lastAttendanceListViewRef.el.appendChild(lastAttendanceElement)
    }

}

registry.category("actions").add("sd_contacts.security_gates", SdContactsSecurityGates);
