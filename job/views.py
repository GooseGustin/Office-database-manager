from django.shortcuts import render, redirect 
from django.views import View
from django.views.generic import (
    CreateView, 
    DetailView, 
    ListView, 
    UpdateView, 
    DeleteView
)
from .models import Job 
# from .forms import JobCreateForm
from staff.models import Staff
from datetime import date as theDate
from inventory.models import Inventory 

ALL_STAFF = Staff.objects.all() 
ALL_INVENTORY = Inventory.objects.filter(deactivate=False) 
ALL_STATUSES = ['Completed', 'Cancelled', 'Incompleted', 'Postponed']

# Create your views here
class JobListView(ListView):
    queryset = Job.objects.all().order_by('-date')# .reverse() 
    template_name = 'job/job_list.html' 
    # print(queryset) 

def listify(obj_string, obj_type): 
    obj_list = []
    if obj_string: 
        for obj_string_item in obj_string.split(','):
            if obj_string_item: 
                obj_list.append(obj_type(obj_string_item))
    return obj_list
    

class JobDetailView(DetailView):
    qqeryset = Job.objects.all() 
    template_name = 'job/job_detail.html' 

    def get_object(self): 
        pk_ = self.kwargs.get('id') 
        obj = Job.objects.get(id=pk_)
        return obj 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['object'] 

        all_job_inv = listify(obj.inventory_used, str)
        all_job_prices = listify(obj.prices, float) 
        all_job_quantities = listify(obj.quantities, int) 
        if (len(all_job_inv) == len(all_job_prices)) and (len(all_job_prices) == (len(all_job_quantities))):
            zipped_details1 = zip(all_job_inv, all_job_prices, all_job_quantities)
            context['zipped1'] = zipped_details1

        other_items, other_costs= listify(obj.other_items, str), listify(obj.other_items_expenses, float)
        if len(other_items) == len(other_costs):
            zipped_details2 = zip(other_items, other_costs)
            context['zipped2'] = zipped_details2

        context['all_staff'] = listify(obj.staff_assigned, str)
        context['battery_serials'] = eval(obj.battery_serials) 
        context['inverter_serials'] = eval(obj.inverter_serials)
        # print(context) 
        return context 


def jobCreateView(request):
    '''I used a FBV instead of a CBV because I had to manually convert 
    some of the form data into models before saving the inventory object
    Update: It's actually because I didn't know how to use CBVs
    ''' 
    template_name = 'job/job_create.html'
    # battery_inv = [good for good in ALL_INVENTORY if 'battery' in good.name.lower()]
    # inverter_inv = [good for good in ALL_INVENTORY if 'inverter' in good.name.lower() ]
    battery_inv = ALL_INVENTORY.filter(type__name='Battery') 
    inverter_inv = ALL_INVENTORY.filter(type__name='Inverter')


    if request.method == 'POST':
        form = request.POST 
        ''' 
        GET FORM DATA 
        '''
        # GET STAFF ASSIGNED
        data = {}
        staff_string = ''
        for staff in ALL_STAFF: 
            try:
                if form[staff.name]:
                    staff_string += staff.name + ','
            except KeyError: 
                continue
        staff_string = staff_string.strip(',') 
        data['staff_assigned'] = staff_string

        # print(goods, prices, quantities)
        data['location'] = form['location']
        if data['location']:
            data['location'] = data['location'].lower()
        data['transportation_cost'] = form['transportation_cost'] 
        data['job_description'] = form['job_description']
        ######################################
        ''' 
        Re-render create page with error message if no transport cost and job description 
        '''
        required = [
            data['staff_assigned'],     
            data['transportation_cost'], 
            data['job_description'], 
            data['location']
        ]
        if ('' in required): #  or (0.00 in required):
            some_error = "Please enter the staff assigned, transportation cost, location and nature of the job"
            context = {
                'all_staff': ALL_STAFF , 
                'all_inventory': ALL_INVENTORY,
                'all_job_statuses': ALL_STATUSES,
                'some_error': some_error,
            }
            return render(request, template_name, context)
        ###################################################
        ''' Extract the goods, prices, and quantities from the form data '''
        # GET INVENTORY USED 
        goods = '' 
        prices = '' 
        quantities = ''
        for inv in ALL_INVENTORY:
            try: 
                good_ = form[inv.name]
                price_ = form[inv.name + '_price']
                quantity_ = form[inv.name + '_quantity']

                if good_ and float(price_) and int(quantity_):
                    goods += inv.name + ','  
                    prices += price_ + ','
                    quantities += quantity_ + ','
                    
            except (KeyError, TypeError, ValueError): 
                continue 

        data['inventory_used'] = goods.strip(',') 
        data['quantities'] = quantities.strip(',') 
        data['prices'] = prices.strip(',') 

        # EXTRACT SERIAL NUMBERS 
        bat_serials = {} 
        for bat in battery_inv: # bat is an inventory 
            # print('Bat name', bat.name)
            val = form.get(f'{bat.name}_serials')
            if val: 
                bat_serials[bat.name] = val
        battery_serials = repr(bat_serials) 

        invt_serials = {}
        for invt in inverter_inv: 
            # print('Invt name', invt.name)
            val = form.get(f'{invt.name}_serials')
            if val: 
                invt_serials[invt.name] = val 
        inverter_serials = repr(invt_serials) 

        data['battery_serials'] = battery_serials 
        data['inverter_serials'] = inverter_serials

        # OTHER DATA 
        data['date'] = form['date'] if form['date'] else theDate.today()
        data['other_items'] = form['other_items']  
        data['other_items_expenses'] = form['other_items_costs'] 
        data['job_status'] = form['job_status'] 
        data['customer_name']= form['customer_name']  
        data['customer_phone'] = form['customer_phone'] 
        data['customer_charge'] = form['customer_charge']  if form['customer_charge']  else 0.00
        data['remark'] = form['remark'] 

        # CALCULATE TOTAL SPENT 
        total = 0.00 
        prices_, quantities_ = listify(data['prices'], float), listify(data['quantities'], int) 
        for i, j in zip(prices_, quantities_): 
            # print('for total', i, j, i*j)
            total += i * j
        other_items_costs_ = listify(data['other_items_expenses'], float)
        for i in other_items_costs_: 
            # print('for total:', i)
            total += i
        total += float(data['transportation_cost'])
        data['total_expenses'] = total 

        ##################################################
        # UPDATE INVENTORY 
        job_inv_list = listify(data['inventory_used'], str)
        job_quan_list = listify(data['quantities'], int) 
        for inv in ALL_INVENTORY:
            # # print(inv.name)
            if inv.name in job_inv_list:
                ind = job_inv_list.index(inv.name) 
                # # print(ind)
                quan = job_quan_list[ind]
                # print('updating inventory', data['quantities'], ind, quan) 
                inv.quantity -= quan
                inv.save()
        ##############################################3

        # CREATE JOB INSTANCE 
        instance = Job(**data) 
        instance.save()
        # print(instance) 
        return redirect('../list/') 
        
    elif request.method == 'GET': 
        # print(ALL_INVENTORY)
        # form = JobCreateForm()
        # print(ALL_STAFF)
        context = {
            'all_staff': Staff.objects.filter(active=True), #ALL_STAFF , 
            'all_inventory': ALL_INVENTORY,
            'all_job_statuses' : ALL_STATUSES,
            'battery_inv': battery_inv, 
            'inverter_inv': inverter_inv,
        }
        return render(request, template_name, context)


class JobUpdateView(View):
    template_name = 'job/job_update.html'
    success_url = '../'

    def get_object(self): 
        pk_ = self.kwargs.get('id') 
        obj = Job.objects.get(id=pk_)
        return obj 

    def get(self, request, *args, **kwargs):
        battery_inv = [good for good in ALL_INVENTORY if 'battery' in good.name.lower()]
        inverter_inv = [good for good in ALL_INVENTORY if 'inverter' in good.name.lower() ]

        # Do not forget *args, **kwargs above 
        object = self.get_object()
        obj_staff = listify(object.staff_assigned, str) 
        obj_inv = listify(object.inventory_used, str) 
        obj_quan = listify(object.quantities, int) 
        quant = []
        for _, inv in enumerate(ALL_INVENTORY):
            if inv.name in obj_inv: 
                ind = obj_inv.index(inv.name)
                quant.append(obj_quan[ind])
            else: quant.append(0)
        zip_inv_quant = zip(ALL_INVENTORY, quant)


        context = {
            'object': object, 
            'all_staff': ALL_STAFF, 
            'all_job_statuses': ALL_STATUSES, 
            'obj_staff': obj_staff, 
            'obj_inv': obj_inv, 
            'obj_date': str(object.date), 
            'zip_inv_quant': zip_inv_quant, 
            'battery_inv': [inv.name for inv in battery_inv], 
            'inverter_inv': [inv.name for inv in inverter_inv], 
            'obj_batt_serials': eval(object.battery_serials), 
            'obj_invt_serials': eval(object.inverter_serials),
        }
        return render(request, self.template_name, context) 

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        form = request.POST 
        ''' 
        GET FORM DATA
        '''
        # GET REQUIRED FIRST - staff assigned, location, transportation cost, and 
        # job description 
        battery_inv = ALL_INVENTORY.filter(type__name='Battery') 
        inverter_inv = ALL_INVENTORY.filter(type__name='Inverter')

        data = {}
        staff_string = ''
        for staff in ALL_STAFF: 
            try:
                if form[staff.name]:
                    staff_string += staff.name + ','
            except KeyError: 
                continue
        staff_string = staff_string.strip(',') 
        data['staff_assigned'] = staff_string

        # GET INVENTORY USED 
        goods = '' 
        prices = '' 
        quantities = ''

        data['location'] = form['location'] 
        data['transportation_cost'] = form['transportation_cost'] 
        data['job_description'] = form['job_description']
        data['date'] = form['date'] if form['date'] else theDate.today()

        ######################################
        ''' 
        Re-render create page with error message if no transport, date, cost and job description 
        '''
        # # # print('Goods sold in creation', goods, type(goods), len(goods))
        required = [
            data['staff_assigned'],     
            data['transportation_cost'], 
            data['job_description'], 
            data['location']
        ]
        if ('' in required) or (0.00 in required):
            # # print('Required', required)

            object = self.get_object()
            obj_staff = listify(object.staff_assigned, str) 
            obj_inv = listify(object.inventory_used, str) 
            obj_quan = listify(object.quantities, int) 
            quant = []
            for _, inv in enumerate(ALL_INVENTORY):
                if inv.name in obj_inv: 
                    ind = obj_inv.index(inv.name)
                    quant.append(obj_quan[ind])
                else: quant.append(0)
            zip_inv_quant = zip(ALL_INVENTORY, quant)

            # print(inverter_inv) 

            some_error = "**Staff assigned, Transportation cost, Location and Nature of the job are required**"
            context = {
                'object': object, 
                'obj_staff': obj_staff, 
                'obj_date': str(object.date), 
                'all_staff': ALL_STAFF , 
                'all_inventory': ALL_INVENTORY,
                'all_job_statuses': ALL_STATUSES,
                'some_error': some_error,
                'battery_inv': [inv.name for inv in battery_inv], 
                'inverter_inv': [inv.name for inv in inverter_inv],
                'obj_batt_serials': eval(object.battery_serials), 
                'obj_invt_serials': eval(object.inverter_serials),

                'obj_inv': obj_inv, 
                'zip_inv_quant': zip_inv_quant, 
                }
            return render(request, self.template_name, context)

        ###################################################
        ''' Extract the goods, prices, and quantities from the form data '''
        for inv in ALL_INVENTORY:
            try: 
                good_ = form[inv.name]
                price_ = form[inv.name + '_price']
                quantity_ = form[inv.name + '_quantity']

                if good_ and float(price_) and int(quantity_):
                    goods += inv.name + ','  
                    prices += price_ + ','
                    quantities += quantity_ + ','
                    
            except (KeyError, TypeError, ValueError): 
                continue 

        # print(goods, prices, quantities)
        data['inventory_used'] = goods.strip(',') 
        data['quantities'] = quantities.strip(',') 
        data['prices'] = prices.strip(',') 

        # EXTRACT SERIAL NUMBERS 
        bat_serials = {} 
        for bat in battery_inv: # bat is an inventory 
            # print('Bat name', bat.name)
            val = form.get(f'{bat.name}_serials')
            if val: 
                val = val.strip().strip(',') 
                bat_serials[bat.name] = val
        battery_serials = repr(bat_serials) 

        invt_serials = {}
        for invt in inverter_inv: 
            # print('Invt name', invt.name)
            val = form.get(f'{invt.name}_serials')
            if val: 
                val = val.strip().strip(',') 
                invt_serials[invt.name] = val
        inverter_serials = repr(invt_serials) 

        data['battery_serials'] = battery_serials 
        data['inverter_serials'] = inverter_serials

        data['other_items'] = form['other_items']  
        data['other_items_expenses']= form['other_items_costs'] 
        data['job_status']  = form['job_status'] 
        data['customer_name'] = form['customer_name']  
        data['customer_phone'] = form['customer_phone'] 
        data['customer_charge'] = form['customer_charge']  if form['customer_charge']  else 0.00
        data['remark'] = form['remark'] 

        ### UPDATE INVENTORYS 
        # Get all inventory in order to loop over them and compare with job inventory 
        # all_inv = Inventory.objects.all() 
        old_inv_list = listify(object.inventory_used, str)
        new_inv_list = listify(data['inventory_used'], str)
        old_quantities_list = listify(object.quantities, int) 
        new_quantities_list = listify(data['quantities'], int)
        
        for inv in ALL_INVENTORY:
            # if inventory name is in job inventory,
            # get quantity difference between the updated and previous quantity values

            # Three possibilities: 
            # # print('Updating inventory') 
            if inv.name in old_inv_list: 
                if inv.name in new_inv_list:
                    # 1. inv.name was in old_list and is also in new_list
                    ind = new_inv_list.index(inv.name)
                    new_quan = new_quantities_list[ind]
                    ind = old_inv_list.index(inv.name)
                    old_quan = old_quantities_list[ind]
                    # # print(inv.name, 'is in both lists', inv.quantity, old_quan, new_quan)
                    diff = int(old_quan) - int(new_quan)
                    inv.quantity += diff 
                else:
                    # 2. inv.name was in old_list but is not in new_list
                    ind = old_inv_list.index(inv.name)
                    old_quan = old_quantities_list[ind]
                    # # print(inv.name, 'is only in old_list', inv.quantity, old_quan)
                    inv.quantity += int(old_quan) 
            elif inv.name in new_inv_list: 
                # 3. inv.name was not in old_list but is now in new_list 
                ind = new_inv_list.index(inv.name)
                new_quan = new_quantities_list[ind]
                # # print(inv.name, 'is only in new_list', inv.quantity, new_quan) 
                inv.quantity -= int(new_quan) 
            inv.save()
        ##############################################3

        # CALCULATE TOTAL SPENT 
        total = 0.00 
        prices_, quantities_ = listify(data['prices'], float), listify(data['quantities'], int) 
        for i, j in zip(prices_, quantities_): 
            # # print('for total', i, j, i*j)
            total += i * j
        other_items_costs_ = listify(data['other_items_expenses'], float)
        for i in other_items_costs_: 
            # # print('for total:', i)
            total += i
        total += float(data['transportation_cost'])
        data['total_expenses'] = total 

        Job.objects.filter(pk=object.id).update(**data)
        # object.has_maintenance_reminder = False 

        # UPDATE REMINDERS 
        object = self.get_object() 

        # if object is updated, check whether the date still matches the 
        # last refill date of the reminder. If not, delete the reminder, 
        # mark the object as having no reminder 
        object_refill_reminder = object.refillreminder_set.first()
        if object_refill_reminder: 
            if object.date != object_refill_reminder.last_refill_date:
                object_refill_reminder.delete()
                object.has_refill_reminder = False 

        object_maintenance_reminder = object.maintenancereminder_set.first()
        if object_maintenance_reminder: 
            if object.date != object_maintenance_reminder.last_maintenance_date:
                object_maintenance_reminder.delete()
                object.has_maintenance_reminder = False 

        # if object is updated, check whether the products and serial nums of the 
        # warranty reminders associated with the object are all still found 
        # in the objects serials records 
        object_warranty_reminders = object.warrantyreminder_set
        for rem in object_warranty_reminders.iterator():
            if (rem.product in object.inventory_used) and (rem.serial_no in object.battery_serials or rem.serial_no in object.inverter_serials): 
                pass
            else: 
                rem.delete()

        object.save()

        return redirect('../') 
        

class JobDeleteView(View):
    template_name = 'job/job_delete.html' 
    success_url = '../../list' 

    def get_object(self):
        id_ = self.kwargs.get('id') 
        object = Job.objects.get(id=id_) 
        return object

    def get(self, request, *args, **kwargs):
        object = self.get_object() 
        return render(request, self.template_name, {'object': object})

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        # Increase the quantities of inventory used in job when the job record is 
        # deleted 
        # Get names of inventory from job, compare with job inventory and 
            # update inventory quantities 
        goods = listify(object.inventory_used, str) 
        quantities_list = listify(object.quantities, int) 

        for inv in ALL_INVENTORY:
            if inv.name in goods:
                ind = goods.index(inv.name) 
                quan = quantities_list[ind]
                inv.quantity += int(quan)
                inv.save()

        object.delete()
        return redirect('../../list/') 

