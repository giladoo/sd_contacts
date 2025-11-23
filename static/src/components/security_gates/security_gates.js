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
import { SdContactsVisitorsDashboard } from "../web/visitors_contacts_web";

export class SdContactsSecurityGates extends Component {
    static template = "sd_contacts.security_gates_template";
    static components = {SdContactsDashboard, SdContactsVisitorsDashboard, Dropdown, DropdownItem, };
    setup(){
        let self = this;
        this.orm = useService('orm')
        this.action = useService("action");
        this.state = useState({
            sendUpdates: 1,
            gate: {name: 'main', id: 1},
            gates: [{name: 'main', id: 1}],
            today: '',
            is_operator: false,
        })

        this.employeeAttendanceData = useRef('employee_attendance_data')
        this.SdContactsDashboardRef = useRef('sd_contacts_dashboard')
        this.todayDate = useRef('today_date')
        this.selectedGate = useRef('selected_gate')
        this.gateLocation = useRef('gate_location')
        this.lastAttendanceListViewRef = useRef('last_attendance_list_view')

        onMounted(async () => {
            let gates = await this.orm.call('hr.attendance', 'get_gates', [false] )
            gates = JSON.parse(gates)
            this.state.gates = gates.gates
            const savedValue = localStorage.getItem('selectedGate');
            const exists = this.state.gates.some(item => item.id == savedValue)
            if (exists ){
                this.state.gate = this.state.gates.filter(item => item.id == savedValue)[0]
            } else {
                this.state.gate = this.state.gates[0]
            }
            // todo: get the gate from local or session. if user opens several panel each for one of gates,
            //      it needed to be saved separately.
            await self.lastAttendanceListViewUpdate()
            this.selectedGate.el.innerHTML = this.state.gate.name
            this.gateLocation.el.innerHTML = this.state.gate.location[1]
            this.todayDate.el.innerHTML = this.state.today
//            this.viewId = await this.orm.call('ir.model.data', '_xmlid_to_res_id', [
//                false,
//                'sd_contacts.gate_attendance_list'
//            ]);
//            console.log('this.viewId', this.viewId)
        })
        this.onEmployeeListClick = this.onEmployeeListClick.bind(this)
        this.onVisitListClick = this.onVisitListClick.bind(this)
        this.onInOutClick = this.onInOutClick.bind(this)
        this.onCounterClick = this.onCounterClick.bind(this)
        this.lastAttendanceListViewUpdate = this.lastAttendanceListViewUpdate.bind(this)
        this.selectGate = this.selectGate.bind(this)
        this.getAttendances = this.getAttendances.bind(this)
        this.sendEmergency = this.sendEmergency.bind(this)

    }
    async onVisitListClick(e, visit_id=0){
        if (visit_id == 0 && e.target.classList.contains('visit_id')){
            visit_id = e.target.id
        }else if (visit_id == 0 && e.target.parentElement.classList.contains('visit_id')){
            visit_id = e.target.parentElement.id
        }
        console.log('onVisitListClick:', visit_id)
        if (visit_id){
        // TODO: show record data on the info box
        }
    }
    async onEmployeeListClick(e, employee_id=0){
        if (employee_id == 0 && e.target.classList.contains('employee_image_id')){
            employee_id = e.target.id
        }else if (employee_id == 0 && e.target.parentElement.classList.contains('employee_image_id')){
            employee_id = e.target.parentElement.id
        }
        if(employee_id){
            let data = await this.orm.call('hr.attendance', 'get_attendance', [false, employee_id,])
            data = JSON.parse(data)
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
        let res_model, domain, context, action_name;
        res_model = "hr.attendance"
        context = {gate_id: this.state.gate.id,
                    list_view_ref: "sd_contacts.gate_attendance_list",
                    search_view_ref: "sd_contacts.gate_attendance_search",
                }

        if(e == 'local_attendances'){
            action_name = _t("Present employees")
            domain = [
                        ['in_gate.location', '=', this.state.gate.location[0]],
                        ['employee_id.work_location_id', '=', this.state.gate.location[0]],
                        ['check_out', '=', false],
                    ]
//            context = {search_default_present: 1}
        } else if(e == 'site_attendances'){
            action_name = _t("Present employees on sites")
            domain = [
                        ['in_gate.location', '!=', this.state.gate.location[0]],
                        ['employee_id.work_location_id', '=', this.state.gate.location[0]],
                        ['check_out', '=', false],
                    ]
//            context = {search_default_present: 1}
        } else if(e == 'left_attendances'){
            action_name = _t("Departed employees")
            domain = [
                        ['employee_id.work_location_id', '=', this.state.gate.location[0]],
                        ['check_out', '!=', false],
                        ['employee_id.hr_icon_display', 'not in', ["presence_present", 'presence_home', 'presence_office', 'presence_other']],
                    ]
            context = {...context, search_default_today: 1}
        } else if(e == 'present_guests'){
            action_name = _t("Present guests")
            domain = [
                        ['in_gate.location', '=', this.state.gate.location[0]],
                        ['employee_id.work_location_id', '!=', this.state.gate.location[0]],
                        ['check_out', '=', false],
                    ]
        } else if(e == 'leave_guests'){
            action_name = _t("Departed guests")
            domain = [
                        ['in_gate.location', '=', this.state.gate.location[0]],
                        ['employee_id.work_location_id', '!=', this.state.gate.location[0]],
                        ['check_out', '!=', false],
                    ]
            context = {...context, search_default_today: 1}
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
                domain: domain,
                context: context,
                target: 'new',
            },
            { onClose: () =>{
//            console.log('this:', this)
            this.lastAttendanceListViewUpdate()
            }
            })
    }
    async onInOutClick(employee_id){
        let data = await this.orm.call('hr.attendance', 'set_attendance', [false, employee_id, this.state.gate.id])
        this.onEmployeeListClick(false, employee_id)
        this.state.sendUpdates = [{id: 4, hr_icon_display: this.state.sendUpdates.hr_icon_display == 'presence_present' ? 'presence_absence' : 'presence_present'}]
    }
    sendUpdates(){
//        console.log('sendUpdates')
    }
    updatePresenceState(){
        let imageStatus = document.querySelectorAll('div.img_div.employee_image_id')
       //todo: if employee is present, add border-success class
    }
    async getAttendances(){
        let lastAttendancesData = await this.orm.call('hr.attendance', 'get_last_attendances', [false, 12, this.state.gate.location[0]] )
        lastAttendancesData = JSON.parse(lastAttendancesData)
        this.state.today = lastAttendancesData.today

        return lastAttendancesData

    }
    async lastAttendanceListViewUpdate(){
        const LAD = await this.getAttendances()
//        console.log('lad:', LAD)
        const lastAttendances = LAD.last_attendances_time
        const counts = LAD.counts
        const lastAttendanceElement = renderToElement("sd_contacts.last_attendance_template", {
            props: { lastAttendances, counts }, this: this, _t: _t
        });
        this.lastAttendanceListViewRef.el.innerHTML = ''
        this.lastAttendanceListViewRef.el.appendChild(lastAttendanceElement)
    }
    async selectGate(gate){
//        console.log('gate:', gate)
        this.state.gate = gate
        this.selectedGate.el.innerHTML = this.state.gate.name
        this.gateLocation.el.innerHTML = this.state.gate.location[1]

        localStorage.setItem('selectedGate', gate.id);
        this.lastAttendanceListViewUpdate()
    }
    async sendEmergency(location){
//        console.log('sendEmergency',this.state.gate, this)
        await this.orm.call('hr.attendance', 'send_emergency', [false, this.state.gate.location[0]] )

    }

}

registry.category("actions").add("sd_contacts.security_gates", SdContactsSecurityGates);
