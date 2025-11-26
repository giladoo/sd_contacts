/** @odoo-module */

import { registry } from "@web/core/registry"
import { Component, useState, useRef, onMounted, onWillUnmount, onWillUpdateProps, xml } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Tooltip } from "@web/core/tooltip/tooltip";

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class SdContactsVisitorsDashboard extends Component {
    setup(){
        let self = this;
        this.action = useService("action");
        this.orm = useService('orm')
        this.newVisitCreate = useRef('new_visit_create')
        this.visitContactsList = useRef('visit_contacts_list')
        this.contactsSearch = useRef('contacts_search')
        this.state = useState({
            visits: [],
            presents: 'presents',
            gateId: this.props.gateId,
            search: [],
            contacts_filtered: [],

        })
        onWillUpdateProps(async (nextProps) => {
//            let data = this.getData()
//            console.log('data 1:', nextProps.sendVisitUpdates, this.props.sendVisitUpdates)
            if(nextProps.sendVisitUpdates != this.props.sendVisitUpdates){
                this.refreshList()
            }

        });
        onMounted(async () => {
            this.refreshList()
            browser.addEventListener('keyup', self._onContactsSearch);

        });
        onWillUnmount(() => {
            browser.removeEventListener('keyup', self._onContactsSearch);

        });
        this._onVisitButton = this._onVisitButton.bind(this);
        this.refreshList = this.refreshList.bind(this);
        this.onVisitsClick = this.onVisitsClick.bind(this);
        this.onShowAllVisits = this.onShowAllVisits.bind(this);
        this._onContactsSearch = this._onContactsSearch.bind(this);

    }
    _onContactsSearch(e){
//        console.log('con _onContactsSearch', e, this.contactsSearch)
//        return
        let contacts_search_value = this.contactsSearch.el.value
        if( e.keyCode == 13){
            this.updateList(this.state.contacts_filtered)
//            console.log('_onContactsSearch:', this.state.contacts_filtered)
            this.state.search = ['']
            this.contactsSearch.el.value = ''
        } else{
            this.state.search = contacts_search_value.toLowerCase().split(' ')
//            console.log('_onContactsSearch:', this.state.contacts_filtered)
//            console.log('search', this.state.search)
            let the_list = this._isInclude(this.state.contacts_filtered, this.state.search[0])
            the_list = this.state.search[1] ? this._isInclude(the_list,this.state.search[1]) : the_list
            the_list = this.state.search[2] ? this._isInclude(the_list,this.state.search[2]) : the_list
            the_list.length > 0 ? this.updateList(the_list) : this.updateList([])
        }

    }
        _isInclude(ar, st){
        return ar.filter(rec => {
                        return ((rec.name ? rec.name.includes(st) : false)
                            || (rec.national_id ? rec.national_id.includes(st) : false)
                            || (rec.mobile_no ? rec.mobile_no.includes(st) : false)
                            || (rec.employee ? rec.employee.includes(st) : false)
                //            || (rec.barcode ? rec.barcode.includes(st) : false)
                                )
        })
    }
    selectFilterItems(search_clear = false){
        if (search_clear){
            this.state.search = ['']
            this.contactsSearch.el.value = ''
        }
        this._onContactsSearch('')
    }
    onShowAllVisits(ev){
        this.state.present = ev.target.checked ? 'presents' : 'all'
        this.refreshList()
    }

    async refreshList(){
        let data = await this.getData()
        this.state.visits = data['visits_list'];
        this.state.contacts_filtered = data['visits_list'];
        this.updateList(this.state.visits)

    }

    updateList(data){
//        if(!data || !this.contactsList){
//            return
//        }
//        console.log('updateList:', data)
        this.visitContactsList.el.innerHTML = ''

        let textColor = ''
        let btnOut = ''
        let name = ''

        let visitListHtml = ''
        data.forEach(rec => {
            if (!rec.check_out){
                textColor = 'text-success'
//                btnOut = `<div class="col-1">
//                                <button id="${rec.id}" class="visit_id_btn px-2 btn btn-fill-custom bg-danger-light fa fa-sign-out">out</button>
//                          </div>
//                          `
            } else{
                textColor = 'text-bg-300'
//                btnOut = `<div class="col-1"></div>`
            }
            name = rec.national_id ? `${rec.name} - ${rec.national_id}` : rec.name
            visitListHtml += `
            <div id="${rec.id}" class="visit_id row border-bottom p-2 mb-1 shadow-sm mx-0 ${textColor} " >
                ${btnOut}
                <div class="col-3"> ${name}</div>
                <div class="col-2"> ${rec.mobile_no || ''}</div>
                <div class="col-2"> ${rec.employee || ''}</div>
                <div class="col-2"> ${rec.check_in}</div>
                <div class="col-2"> ${rec.check_out || ''}</div>
            </div>
            `
        })

        visitListHtml += '<div style="height: 100px;"></div>'
        this.visitContactsList.el.innerHTML = visitListHtml;

    }
    async getData(){
        let data = await this.orm.call('sd_contacts.visits', 'contact_web', [false, this.state.present], {})
        return JSON.parse(data)
    }
    async onVisitsClick(e){
        let visit_id = 0;
        this.state.gateId = this.props.gateId
        if (e.target.classList.contains('visit_id_btn')){
            visit_id = e.target.id
        }else if (e.target.parentElement.classList.contains('visit_id_btn')){
            visit_id = e.target.parentElement.id
        }
        if (visit_id){
            await this.orm.call('sd_contacts.visits', 'set_check_out', [false, visit_id, this.state.gateId])
            this.refreshList()
        }
    }
    _onVisitButton(name=''){
        let res_model, views, view_mode, domain, context, action_name;
        this.state.gateId = this.props.gateId
        if(name == 'new'){
            res_model = "sd_contacts.visits"
            action_name = _t("New visit")
            views = [[false, "form"],]
            view_mode = "form"
            domain = []
            context = {'default_in_gate': this.state.gateId}
        } else if(name == 'visits'){
            res_model = "sd_contacts.visits"
            action_name = _t("Visits List")
            views = [[false, "list"],]
            view_mode = "list"
            domain = []
            context = {'search_default_today': 1, 'search_default_name_group': 1}
        }

        this.action.doAction(
            {
                type: "ir.actions.act_window",
                name: action_name,
                res_model: res_model,
                views: views,
                view_mode: view_mode,
                domain: domain,
                context: context,
                target: 'new',
            },
            { onClose: () =>{
//            console.log('this:', this)
            this.refreshList()
            }
            })
    }
}

SdContactsVisitorsDashboard.template = "sd_contacts.visitors_contacts_template";
SdContactsVisitorsDashboard.components = { Dropdown, DropdownItem };
SdContactsVisitorsDashboard.props = { gateId: Number, sendVisitUpdates: Number }
registry.category("actions").add("sd_contacts.visitors_contacts_dashboard", SdContactsVisitorsDashboard);

