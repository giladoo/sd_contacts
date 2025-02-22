/** @odoo-module **/

import { Component , useState, useRef, onMounted, onWillUnmount, xml} from "@odoo/owl";
import { registry } from "@web/core/registry"
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { rpc } from "@web/core/network/rpc";

export class SdContactsContactList extends Component {
    static template = "sd_contacts.contact_list_template";
    static props = {};
    static components = { Dropdown, DropdownItem };
    setup(){
        let self = this;

        this.contactsSearch = useRef('contacts_search')
        this.contactsList = useRef('contacts_list')
        this.contactsPhone = useRef('contacts_phone')
        this.contactsEmail = useRef('contacts_email')
        this.contactsCompanies = useRef('contacts_companies')
        this.contactsSelectLocation = useRef('contacts_select_location')
        this.selectedLocation = useRef('selected_location')
        this.contactsSelectDepartment = useRef('contacts_select_department')
        this.selectedDepartment = useRef('selected_department')
        this.selectedProject = useRef('selected_project')
        this.searchClear = useRef('search_clear')
        this.popover = usePopover(Tooltip);
        this.state = useState({
            labels: {
                title: _t('Employees Contact Information'),
                name: _t('Name'),
                depjob: `${_t('Job')} ${_t('Department')}`,
                location_project: `${_t('Location')} ${_t('Project')}`,
//                location: _t('Location'),
//                project: _t('Project'),
                phone: _t('Phone'),
                email: _t('Email'),
                },
            employees: [],
            contacts_filtered: [],
            departments: ['Deps...'],
            locations: ['Locs...'],
            projects: ['Proj...'],
            companies: [],
            search: [''],
            selectedDepartment: _t('All'),
            selectedLocation: _t('All'),
            selectedProject: _t('All'),
        })
        this.contacts_select_location = useRef('contacts_select_location')
        onMounted(async () => {
//            console.log('con onMounted 1')
            browser.addEventListener('keyup', self._onContactsSearch);
            browser.addEventListener('click', self._copyToClipBoard)
//            self.contactsCompanies.el.addEventListener('click', self._onContactsCompanies)

//            console.log('con onMounted 2')
            this.selectedLocation.el.innerHTML = _t('Locations')
            this.selectedDepartment.el.innerHTML = _t('Departments')
            this.selectedProject.el.innerHTML = _t('Projects')

//            console.log('con onMounted 3')

        await rpc('/employee/contactdata', {})
            .then(data => JSON.parse(data))
            .then(data=> {
                console.log('data:', data)
                self.state.employees = data['contact_list'];
                self.state.contacts_filtered = data['contact_list'];
                self.state.companies = data['company_list'];
                self.state.locations = data['location_list'];
                self.state.departments = data['department_list'];
                self.state.projects = data['project_list'];
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
        console.log('state', this.state)
        this._onContactsSearch = this._onContactsSearch.bind(this);
        this._copyToClipBoard = this._copyToClipBoard.bind(this);
        this._onContactsCompanies = this._onContactsCompanies.bind(this);
        this._onContactsSelectLocation = this._onContactsSelectLocation.bind(this);
        this._onContactsSelectDepartment = this._onContactsSelectDepartment.bind(this);
    }
    selectLocation(location){
        this.state.selectedLocation = location
        this.selectFilterItems()
    }
    selectDepartment(department){
        this.state.selectedDepartment = department
        this.selectFilterItems()
    }
    selectProject(project){
        this.state.selectedProject = project
        this.selectFilterItems()
    }
    selectFilterItems(search_clear = false){
        let location = this.state.selectedLocation
        let department = this.state.selectedDepartment
        let project = this.state.selectedProject
        if (search_clear){
            location = _t('All')
            department = _t('All')
            project = _t('All')
            this.state.search = ['']
            this.contactsSearch.el.value = ''

        }

        if (location != _t('All')){
            this.selectedLocation.el.innerHTML =  `${location}`
            this.state.contacts_filtered = this.state.employees.filter(rec => rec.work_location == location)
        } else {
            this.selectedLocation.el.innerHTML = _t('Locations')
            this.state.selectedLocation = _t('All')
            this.state.contacts_filtered = this.state.employees

        }
        if (department != _t('All')){
            this.selectedDepartment.el.innerHTML =  `${department}`
            this.state.contacts_filtered = this.state.contacts_filtered
                .filter(rec => rec.department == department || rec.parent_department_1 == department )

        } else {
            this.selectedDepartment.el.innerHTML = _t('Department')
            this.state.selectedDepartment = _t('All')
            this.state.contacts_filtered = this.state.contacts_filtered
        }

        if (project != _t('All')){
            this.selectedProject.el.innerHTML =  `${project}`
            this.state.contacts_filtered = this.state.contacts_filtered
                .filter(rec => rec.project == project )

        } else {
            this.selectedProject.el.innerHTML = _t('Projects')
            this.state.selectedProject = _t('All')
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
    updateList(data){
        if(!data || !this.contactsList){
            return
        }
        let statusBorder = 'border-gray';
//        console.log('updateList', data)
        this.contactsList.el.innerHTML = '';
//                        <div class="col-2 px-1 img_div "><img src="/web/image?model=hr.employee&amp;id=${rec.id}&amp;field=avatar_128"/></div>
        let contactsListHtml = ''
        data.forEach(rec => {
            let url = '';
            if (rec.im_status == 'online'){
                statusBorder = 'border-success border-2'
            } else if (rec.im_status == 'away'){
                statusBorder = 'border-warning border-2'
            } else {
                statusBorder = ''
            }

//            url = `/web/image?model=hr.employee.public&amp;id=${rec.id}&amp;field=avatar_128`
            url = `/employee/contactsimage/${rec.id}/`
            contactsListHtml += `
            <div class="col-12 row mx-0 mb-1 px-0 border-bottom align-items-center shadow-sm">

                <div class="col-2 col-md-1 px-1 py-1">
                    <div class="img_div rounded-circle border  p-1 ${statusBorder}"
                    style="background-image: url(${url})"></div>
                </div>

                <div class="row col-11 col-md-11 mx-0 p-3 p-md-0 align-items-center">

                    <div class="row col-5 col-md-6 mx-0 mb-1 px-0 align-items-center">
                        <div class="col-12 col-md-6 px-1 h6 text-center "> ${rec.name}</div>
                        <div class="col-12 col-md-6 px-1 text-center">
                            <div class="h6" >${rec.job_title|| ''}</div>
                            <div class="small employee_department_name cursor-pointer">${rec.department || ''}</div>
                            <div class="small">${this.state.companies.length > 1 ? rec.company : ''}</div>
                        </div>
                    </div>

                    <div class="col-3 col-md-2 mx-0 mb-1 px-0">
                        <div ref="contacts_location" class="col-12  px-1 h6 text-center  employee_location_name cursor-pointer"> ${rec.work_location || ''}</div>
                        <div ref="contacts_project" class="col-12  px-1 h6 text-center  employee_project_name cursor-pointer"> ${rec.project || ''}</div>
                    </div>
                    <div class="row col-4 col-md-4 mx-0 mb-1 px-0">
                        <div ref="contacts_phone" class="copy_to_clip_board col-12 col-md-3 px-1 h6 text-center"> ${rec.work_phone || ''}</div>
                        <div ref="contacts_email" class="copy_to_clip_board contact_email col-12 col-md-6 px-1  text-center small " >
                           ${rec.work_email || ''} </div>
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
        }    }
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

registry.category("public_components").add("sd_contacts.contact_list_component", SdContactsContactList);