/** @odoo-module */
import publicWidget from "web.public.widget";
const { useState } = owl.hooks;

publicWidget.registry.SdEmployeeContacts = publicWidget.Widget.extend({
    selector: ".sd_employee_contacts",
    events:{
        "keyup .contacts_search": "_onContactsSearch",
    },
    start(){
        this.contacts_list = this.el.querySelector('.contacts_list')
        this.contacts_search = this.el.querySelector('.contacts_search')
        this.contacts_search_keys = this.el.querySelector('.contacts_search_keys')

        this.state = useState({
            employees: [],
            search: [''],
        })
        console.log('sd_employee_contacts')
        this._rpc({
            model: 'hr.employee',
            method: 'search_read',
            kwargs: {
                    domain: [],
                    fields: ['id', 'name', 'work_phone', 'work_email', 'department_id', 'job_title'],
                },
        }).then(data=> {
            this.state.employees = data;
            console.log('E:', this.state.employees)
            this.updateList(data)
        })
    },
    _onContactsSearch(e){
//        console.log('_onContactsSearch', e)
        let contacts_search_value = this.contacts_search.value
        if( e.keyCode == 13){
            this.updateList(this.state.employees)
            this.state.search = ['']
            this.contacts_search.value = ''
        } else{
            this.state.search = contacts_search_value.split(' ')
            let the_list = this._isInclude(this.state.employees,this.state.search[0])
            the_list = this.state.search[1] ? this._isInclude(the_list,this.state.search[1]) : the_list
            the_list = this.state.search[2] ? this._isInclude(the_list,this.state.search[2]) : the_list
            the_list.length > 0 ? this.updateList(the_list) : this.updateList([])
        }

    },
    updateList(data){
        if(!data || !this.contacts_list){
            return
        }
        this.contacts_list.innerHTML = '';
//                        <div class="col-2 px-1 img_div "><img src="/web/image?model=hr.employee&amp;id=${rec.id}&amp;field=avatar_128"/></div>

        data.forEach(rec => {
            this.contacts_list.innerHTML += `
            <div class="col-12 row mx-0 mb-1 px-0 border-bottom align-items-center shadow-sm">
                <div class="col-3 col-md-2 py-1">
                    <div class="img_div rounded-circle border p-1 border-dark" style="background-image: url(/web/image?model=hr.employee&amp;id=${rec.id}&amp;field=avatar_128)"></div>
                </div>
                <div class="col-4 col-md-3 px-1 text-center "> ${rec.name}</div>
                <div class="col-3 col-md-3 d-none d-md-block px-1 text-center">
                    <div >${rec.job_title|| ''}</div>
                    <div class="small">${rec.department_id[1] || ''}</div>
                </div>
                <div class="col-2 col-md-1 px-1 text-center"> ${rec.work_phone || ''}</div>
                <div class="col-2 col-md-2 px-1 d-none d-md-block text-center small"> ${rec.work_email || ''}</div>
            </div>
            `
        })
    },
    _isInclude(ar, st){
//        console.log(ar.filter(rec => {
//        return rec.name ? rec.name.includes(st) : false
//            || rec.work_phone ? rec.work_phone.includes(st) : false
//            || rec.work_email ? rec.work_email.includes(st) : false
//        }))
        return ar.filter(rec => {
        return ((rec.name ? rec.name.includes(st) : false)
            || (rec.work_phone ? rec.work_phone.includes(st) : false)
            || (rec.work_email ? rec.work_email.includes(st) : false))
        })
    },

})

export default publicWidget.registry.SdEmployeeContacts;