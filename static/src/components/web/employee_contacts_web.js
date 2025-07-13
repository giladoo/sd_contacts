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

export class SdContactsDashboard extends Component {
//    static template = "sd_contacts.contacts_template";
//    static components = { Dropdown, DropdownItem };
    setup(){
//        super.setup();
        let self = this;
        this.orm = useService('orm')
        this.contactsSearch = useRef('contacts_search')
        this.contactsList = useRef('contacts_list')
        this.contactsPhone = useRef('contacts_phone')
        this.contactsEmail = useRef('contacts_email')
        this.contactsCompanies = useRef('contacts_companies')
        this.contactsSelectLocation = useRef('contacts_select_location')
        this.selectedLocation = useRef('selected_location')
        this.contactsSelectDepartment = useRef('contacts_select_department')
        this.selectedDepartment = useRef('selected_department')
        this.searchClear = useRef('search_clear')
        this.popover = usePopover(Tooltip);
        this.state = useState({
            employees: [],
            contacts_filtered: [],
            departments: ['q'],
            locations: ['w'],
            companies: [],
            search: [''],
            selectedDepartment: _t('All'),
            attendances: [],
        })
        onWillUpdateProps(async (nextProps) => {
            let images
            images = self.contactsList.el.querySelectorAll('.img_div')
//            console.log('nextProps', self, images)
            await self.orm.call('hr.employee', 'contact_web', [[]], {})
                .then(data => JSON.parse(data))
                .then(data=> {
                    self.state.employees = data['contact_list'];
                    self.state.attendances = data['attendances'];
                })
            console.log('aaaa', self.state.employees[10])
            images.forEach(r => {
                r.classList.remove('border-success', 'border-warning', 'border-gray', 'border-3')
                const rec = self.state.employees.find(i => i.id == r.id)
                const words = self.setImageClass(rec).split(' ')


                r.id == 4 ? console.log('bbb', words) : ''
//                console.log('bbb', self.setImageClass(quoted))
                r.classList.add(...words)
            })

        });
        onMounted(async () => {
            browser.addEventListener('keyup', self._onContactsSearch);
            browser.addEventListener('click', self._copyToClipBoard)
            self.contactsCompanies.el.addEventListener('click', self._onContactsCompanies)
//            self.contactsSelectLocation.el.addEventListener('click', self._onContactsSelectLocation)
//            self.contactsSelectDepartment.el.addEventListener('click', self._onContactsSelectDepartment)

            this.selectedLocation.el.innerHTML = _t('Location')
            this.selectedDepartment.el.innerHTML = _t('Department')
//        await self.orm.searchRead('hr.employee',
//                                [],
//                                ['id', 'name', 'work_phone', 'work_email', 'department_id', 'job_title'],{order: 'sequence'})
            await self.orm.call('hr.employee', 'contact_web', [[]], {})
                .then(data => JSON.parse(data))
                .then(data=> {
                    self.state.employees = data['contact_list'];
//                    console.log('employees\n', self.state.employees)
                    self.state.contacts_filtered = data['contact_list'];
                    self.state.companies = data['company_list'];
                    self.state.locations = data['location_list'];
                    self.state.departments = data['department_list'];
                    self.state.attendances = data['attendances'];
                    self.updateList(self.state.employees)
                    if (self.state.companies.length > 1){
                        self.contactsCompanies.el.classList.remove('d-none')
                        self.updateCompanyList(self.state.companies)
                        let e = Object();
                        e['target'] = 'all'
                        self._onContactsCompanies(e)
                    }
                })
        });
        onWillUnmount(() => {
//                    console.log('con onWillUnmount')

            browser.removeEventListener('keyup', self._onContactsSearch);
            browser.removeEventListener('click', self._copyToClipBoard)
            self.contactsCompanies.el.removeEventListener('click', self._onContactsCompanies)
//            self.contactsSelectLocation.el.removeEventListener('click', self._onContactsSelectLocation)
//            self.contactsSelectDepartment.el.removeEventListener('click', self._onContactsSelectDepartment)

        });
        this._onContactsSearch = this._onContactsSearch.bind(this);
        this._copyToClipBoard = this._copyToClipBoard.bind(this);
        this._onContactsCompanies = this._onContactsCompanies.bind(this);
        this._onContactsSelectLocation = this._onContactsSelectLocation.bind(this);
        this._onContactsSelectDepartment = this._onContactsSelectDepartment.bind(this);
    }
    sendUpdates(){
        console.log('getUpdates')
    }
    selectLocation(location){
        this.state.selectedLocation = location
        this.selectFilterItems()
    }
    selectDepartment(department){
        this.state.selectedDepartment = department
        this.selectFilterItems()
    }
    selectFilterItems(search_clear = false){
        let location = this.state.selectedLocation
        let department = this.state.selectedDepartment
        if (search_clear){
            location = _t('All')
            department = _t('All')
            this.state.search = ['']
            this.contactsSearch.el.value = ''

        }

        if (location != _t('All')){
            this.selectedLocation.el.innerHTML =  `${location}`
            this.state.contacts_filtered = this.state.employees.filter(rec => rec.work_location == location)
        } else {
            this.selectedLocation.el.innerHTML = _t('Location')
            this.state.selectedLocation = _t('All')
            this.state.contacts_filtered = this.state.employees

        }
        if (department != _t('All')){
            this.selectedDepartment.el.innerHTML =  `${department}`
            this.state.contacts_filtered = this.state.contacts_filtered.filter(rec => rec.department == department)

        } else {
            this.selectedDepartment.el.innerHTML = _t('Department')
            this.state.selectedDepartment = _t('All')
            this.state.contacts_filtered = this.state.contacts_filtered
        }


        this._onContactsSearch('')
    }
    _onContactsSelectLocation(e){
        console.log('_onContactsSelectLocation:', e)
    }
    _onContactsSelectDepartment(e){
        console.log('_onContactsSelectDepartment:', e)
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
    setImageClass(rec){
        let res;
//        if (["presence_present", "presence_out_of_working_hour"].includes(rec.hr_icon_display)){
        if (["presence_present",].includes(rec.hr_icon_display)){
            res = 'border-success border-3'
        } else if (rec.hr_icon_display == 'away' || this.state.attendances.includes(rec.id)){
            res = 'border-warning border-3'
        } else {
            res = 'border-gray'
        }
        return res
    }
    updateList(data){
        if(!data || !this.contactsList){
            return
        }
        let statusBorder = 'border-gray';
//        console.log('updateList', data)
        this.contactsList.el.innerHTML = '';
//                        <div class="col-2 px-1 img_div employee_image_id " id="${rec.id}"><img src="/web/image?model=hr.employee&amp;id=${rec.id}&amp;field=avatar_128"/></div>
        let contactsListHtml = ''
        data.forEach(rec => {
            statusBorder = this.setImageClass(rec)

            contactsListHtml += `
            <div class="col-12 row mx-0 mb-1 px-0 border-bottom align-items-center shadow-sm">
                <div class="col-2 col-md-2 px-1 py-1 employee_image_id" id="${rec.id}">
                    <div class="img_div rounded-circle border  p-1 ${statusBorder} employee_image_id" id="${rec.id}"
                    style="background-image: url(/web/image?model=hr.employee.public&amp;id=${rec.id}&amp;field=avatar_128)"></div>
                </div>

                <div class="row col-10 col-md-10 p-3 p-md-0">

                    <div class="row col-6 col-md-6 mx-0 mb-1 px-0 ">
                        <div class="col-12 col-md-6 px-1 h6 text-center "> ${rec.name}</div>
                        <div class="col-12 col-md-6 px-1 text-center">
                            <div class="h6" >${rec.job_title|| ''}</div>
                            <div class="small  employee_department_name cursor-pointer">${rec.department || ''}</div>
                            <div class="small">${this.state.companies.length > 1 ? rec.company : ''}</div>
                        </div>
                    </div>

                    <div class="row col-6 col-md-6 mx-0 mb-1 px-0">
                        <div ref="contacts_location" class="col-12 col-md-3 px-1 h6 text-center  employee_location_name cursor-pointer">
                            ${rec.work_location || ''}
                        </div>
                        <div ref="contacts_phone" class="copy_to_clip_board col-12 col-md-3 px-1 h6 text-center">
                            ${rec.work_phone || ''}
                         </div>
                        <div ref="contacts_email" class="copy_to_clip_board contact_email col-12 col-md-6 px-1  text-center small " >
                           ${rec.work_email || ''}
                        </div>
                    </div>

                </div>
            </div>
            `
        })

        contactsListHtml += '<div style="height: 100px;"></div>'
        this.contactsList.el.innerHTML = contactsListHtml;

    }
    updateCompanyList(data){
        this.contactsCompanies.el.innerHTML += `
            <div class="contacts_companies_btn contacts_companies_all btn btn-primary border-0 m-1 text-center ">All</div>
        `
        data.forEach(rec => {
            this.contactsCompanies.el.innerHTML += `
                <div class="contacts_companies_btn btn btn-primary border-0 m-1 text-center "> ${rec}</div>
            `
        })
    }
    _onContactsCompanies(ev){
        let contactsCompany = false
        let target = ev.target
        if (target == 'all' || target.classList.contains('contacts_companies_all')){
            contactsCompany = 'all';
            target = this.el.querySelector('.contacts_companies_all')
            this.state.contacts_filtered =  this.state.employees
        }
        else if (target.classList.contains('contacts_companies_btn')){
            contactsCompany = ev.target.innerText;
            this.state.contacts_filtered =  this.state.employees.filter(rec => rec.company == contactsCompany)
        }
        if (contactsCompany){
            let selected = this.contactsCompanies.el.querySelectorAll('.contacts_companies_selected')
            selected.forEach(rec => rec.classList.remove('contacts_companies_selected'))
            target.classList.add('contacts_companies_selected')
            this.updateList(this.state.contacts_filtered)
        }


    }
    showTooltip(target) {
        this.popover.open(target, { tooltip: _t("Copied") });
        browser.setTimeout(this.popover.close, 800);
    }
    _copyToClipBoard(e){
        let copyText = e.target.innerText;
        let target = e.target
        if (target.classList.contains('copy_to_clip_board')){
            navigator.clipboard.writeText(target.innerText);
            this.showTooltip(target)

        }
        else if (target.classList.contains('employee_department_name')){
            this.selectDepartment(target.innerText)
        }
        else if (target.classList.contains('employee_location_name')){
            this.selectLocation(target.innerText)
        }
        else if (target.classList.contains('employee_project_name')){
            this.selectProject(target.innerText)
        }
    }
    _isInclude(ar, st){
//        console.log(ar.filter(rec => {
//        return rec.name ? rec.name.includes(st) : false
//            || rec.work_phone ? rec.work_phone.includes(st) : false
//            || rec.work_email ? rec.work_email.includes(st) : false
//        }))
        return ar.filter(rec => {
        return ((rec.name ? rec.name.includes(st) : false)
            || (rec.work_phone ? rec.work_phone.includes(st) : false)
            || (rec.work_location ? rec.work_location.includes(st) : false)
            || (rec.work_email ? rec.work_email.includes(st) : false))
        })
    }
}

SdContactsDashboard.template = "sd_contacts.contacts_template";
//SdContactsDashboard.template = "sd_contacts.contacts_template_website_new";
SdContactsDashboard.components = { Dropdown, DropdownItem };

//SdContactsDashboard.template = xml`<div>,,,,xml....</div>`;

registry.category("actions").add("sd_contacts.contacts_dashboard", SdContactsDashboard);
//registry.add("w_sd_contacts_contacts_dashboard", SdContactsDashboard);


//registry.category("public_components").add("sd_contacts.contact_list_component_web", SdContactsDashboard);




//export default SdContactsDashboard;
