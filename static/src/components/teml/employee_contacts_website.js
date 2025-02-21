/** @odoo-module **/
//import { SdContactsDashboard } from "../web/employee_contacts_web";
import { registry } from "@web/core/registry";
import { mount } from "@odoo/owl";
import { renderToElement } from "@web/core/utils/render";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from '@web/core/network/rpc';
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";


publicWidget.registry.EmployeeContacts = publicWidget.Widget.extend({
    selector: ".sd_contacts_contacts_dashboard",
    async start() {
            this.loadTable({})
            this.contactsSearch = this.el.querySelector('.contacts_search')
            this.contactsList = this.el.querySelector('.contacts_list')
            this.contactsPhone = this.el.querySelector('.contacts_phone')
            this.contactsEmail = this.el.querySelector('.contacts_email')
            this.contactsCompanies = this.el.querySelector('.contacts_companies')
            this.contactsSelectLocation = this.el.querySelector('.contacts_select_location')
            this.selectedLocation = this.el.querySelector('.selected_location')
            this.contactsSelectDepartment = this.el.querySelector('.contacts_select_department')
            this.selectedDepartment = this.el.querySelector('.selected_department')
            this.searchClear = this.el.querySelector('.search_clear')


        console.log('EmployeeContacts', this)
        this.state = {
            employees: [],
            contacts_filtered: [],
            departments: ['q'],
            locations: ['w'],
            companies: [],
            search: [''],
            selectedDepartment: _t('All'),
            selectedLocation: _t('All'),
        }
//            mount(SdContactsDashboard, {}, this.$el)
//        return this._super(...arguments);
//    this.selectFilterItems =
    },
    selectFilterItems(search_clear = false){
        let location = this.state.selectedLocation
        let department = this.state.selectedDepartment
        if (search_clear){
            location = _t('All')
            department = _t('All')
            this.state.search = ['']
            this.contactsSearch.value = ''

        }

        if (location != _t('All')){
//            this.selectedLocation.innerHTML =  `${location}`
//            this.state.contacts_filtered = this.state.employees.filter(rec => rec.work_location == location)
        } else {
//            this.selectedLocation.innerHTML = _t('Location')
//            this.state.selectedLocation = _t('All')
//            this.state.contacts_filtered = this.state.employees

        }
        if (department != _t('All')){
//            this.selectedDepartment.innerHTML =  `${department}`
//            this.state.contacts_filtered = this.state.contacts_filtered.filter(rec => rec.department == department)

        } else {
//            this.selectedDepartment.innerHTML = _t('Department')
//            this.state.selectedDepartment = _t('All')
//            this.state.contacts_filtered = this.state.contacts_filtered
        }


        this._onContactsSearch('')
    },
    _onContactsSearch(a){
        console.log(a)
    },
    loadTable(data){
            const contacts_template_1 = renderToElement(
                'sd_contacts.website_contacts_template', {
                this: this,
//                widget: this,
//                val: this.rating_avg,
            });
            console.log('template:',contacts_template_1, this )
            this.$el.empty().html(contacts_template_1);
    },
});

export default publicWidget.registry.EmployeeContacts