from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView, 
    DetailView, 
    ListView, 
    UpdateView, 
    DeleteView
)
from django.views import View
from .models import Sale 
from inventory.models import Inventory 
# from .forms import SaleCreationForm 

from datetime import date as theDate 

# Create your views here
def listify(obj_string, obj_type): 
    obj_list = []
    for obj_string_item in obj_string.split(','):
        if obj_string_item: 
            obj_list.append(obj_type(obj_string_item))
    return obj_list
  

class SaleListView(ListView):
    template_name = 'sale/sale_list.html'
    queryset = Sale.objects.all().order_by('-date')#.reverse()


class SaleDetailView(DetailView):
    template_name = 'sale/sale_detail.html'
    queryset = Sale.objects.all() 
    
    def get_object(self):
        pk_ = self.kwargs.get('id') 
        obj = Sale.objects.get(pk=pk_) 
        return obj 


def saleDetailView(request, id):
    ''' 
    Most of the attibutes of the Sale model are stored as strings, so 
    they will be treated as strings -- split them up, convert to 
    appropriate types and then pass to the template. 
    '''
    # # print('IN DETAIL')
    template_name = 'sale/sale_detail.html' 
    object = Sale.objects.get(id=id) 

    all_sale_inv = list(object.goods_sold.split(','))
    sale_goods_list = listify(object.goods_sold, str)
    battery_inv = [good for good in sale_goods_list if 'battery' in good.lower()]
    inverter_inv = [good for good in sale_goods_list if 'inverter' in good.lower()]

    # # print(all_sale_inv) 
    for i, inv in enumerate(all_sale_inv[:]):
        all_sale_inv[i] = inv.strip()
    all_sale_prices = list(object.prices.split(',')) 
    all_sale_quantities = list(object.quantities.split(',')) 
    for i in range(len(all_sale_prices)):
        # # # print(all_sale_prices) 
        all_sale_prices[i] = float(all_sale_prices[i]) 
        all_sale_quantities[i] = int(all_sale_quantities[i]) # 

    indexes = list(range(len(all_sale_inv))) 
    # print(indexes) 
    # print(all_sale_inv)
    # print('Prices', all_sale_prices) 
    # print(all_sale_quantities) 
    zipped_details = zip(all_sale_inv, all_sale_prices, all_sale_quantities)
    
    context = {
        'object': object, 
        'indexes': indexes, 
        'zipped': zipped_details, 
        'battery_inv': battery_inv, 
        'inverter_inv': inverter_inv, 
        'batt_serials': eval(object.battery_serials), 
        'invt_serials': eval(object.inverter_serials), 
    }

    return render(request, template_name, context)     


def saleCreateView(request):
    '''
    Create a sale, store the goods sold, the customer's details and the date
    The data from the form is collected, converted to and stored as strings
    The quantity of inventory sold should be deducted from the amount in stock
    ''' 
    # print('IN CREATE')
    template_name = 'sale/sale_create.html' 
    all_inv = Inventory.objects.filter(deactivate=False)
    all_inv_names = [inv for inv in all_inv]
    battery_inv = all_inv.filter(type__name='Battery')
    inverter_inv = all_inv.filter(type__name='Inverter')

    if request.method == 'POST': 
        # form = {}
        form = request.POST  
        # # print(form) 
        
        goods = '' 
        prices = '' 
        quantities = ''
        total = 0.00 
        details = '' 

        #########################33
        ''' Extract the goods, prices, and quantities from the form data '''
        for inv in all_inv_names:
            try: 
                good_ = form.get(inv.name)
                price_ = form.get(inv.name + '_price')
                quantity_ = form.get(inv.name + '_quantity') 
                # print('Creation:', inv.name, good_, price_, quantity_, type(quantity_)) 

                if good_ and float(price_) and int(quantity_):
                    # print('Actual Creation:', inv.name, good_, price_, quantity_) 
                    goods += f'{inv.name},'  
                    prices += f'{price_},'
                    quantities += f'{quantity_},'
                    total += (float(price_) * int(quantity_))                
                    
            except (KeyError, TypeError, ValueError): 
                continue 

        goods = goods.removesuffix(',') 
        prices = prices.removesuffix(',') 
        quantities_string = quantities.removesuffix(',') 
        quantities_list = listify(quantities_string, int) 
        
        ##################################################
        '''Update Inventory'''
        # all_inv = Inventory.objects.all() 
        # # print(all_inv)
        goods_list = listify(goods, str)
        for inv in all_inv:
            if inv.name in goods_list:
                ind = goods_list.index(inv.name) 
                quan = quantities_list[ind]
                inv.quantity -= int(quan)
                inv.save()
        ##############################################3

        # Get rest of form data and create sale instance
        # Get list of serial nos, compare with number of inventories

        bat_serials = {} 
        for bat in battery_inv: 
            if bat.name in goods: 
                val = form.get(f'{bat.name}_serials')
                valid = form.get(f'{bat.name}')
                if val and valid: 
                    val = val.strip().strip(',') 
                    bat_serials[bat.name] = val 
                print('BAT_SERIALS', bat_serials) 
        battery_serials = repr(bat_serials) 

        invt_serials = {}
        for invt in inverter_inv: 
            print('Goods', goods, invt.name)
            if invt.name in goods: 
                val = form.get(f'{invt.name}_serials')
                valid = form.get(f'{invt.name}')
                if val and valid: 
                    val = val.strip().strip(',') 
                    invt_serials[invt.name] = val
        inverter_serials = repr(invt_serials) 

        #####################################
        # Re-render create page with error message if no goods were actually sold
        quantity_serial_tally = True 
        for inv in all_inv:
            try:
                quantity_ = form.get(inv.name + '_quantity') 
                if len(listify(bat_serials[inv.name], str)) > int(quantity_): 
                    quantity_serial_tally = False
                elif len(listify(invt_serials[inv.name], str)) > int(quantity_): 
                    quantity_serial_tally = False 
            except (KeyError, AttributeError, ValueError): 
                pass 
            
        refresh = False 
        if not quantity_serial_tally: 
            no_good_error = '**The serial numbers cannot be more than the quantities of goods sold**'
            refresh = True 
        if goods == '':
            no_good_error = 'Please select one or more goods and enter correct prices and quantities'
            refresh = True 
        if refresh: 
            context = {
                'all_inv_names': all_inv_names, 
                'no_good_error': no_good_error,
                'battery_inv': battery_inv, 
                'inverter_inv': inverter_inv, 
            }
            return render(request, template_name, context)
    
        #################################

        customer_name = form.get('customer_name') 
        customer_phone = form.get('customer_phone') 
        date = form.get('date') 
        details = form.get('details')

        if not date:
            date = theDate.today()

        instance = Sale.objects.create(
            goods_sold = goods, 
            prices = prices,
            total=total, 
            quantities = quantities_string, 
            battery_serials=battery_serials,
            inverter_serials=inverter_serials, 
            customer_name=customer_name, 
            customer_phone=customer_phone, 
            date=date, 
            details=details
        )
        instance.save() 
        # print('Done with create')
        return redirect('../list/')

    elif request.method == 'GET': 
        context = {
            'all_inv_names' : all_inv_names, 
            'battery_inv': battery_inv, 
            'inverter_inv': inverter_inv, 
            }
        return render(request, template_name, context)


def saleUpdateView(request, id):
    # print('IN UPDATE')
    object = Sale.objects.get(id=id) 
    template_name = 'sale/sale_update.html' 
    object = Sale.objects.get(id=id) 
    all_sale_inv = Inventory.objects.filter(deactivate=False)
    all_goods = object.goods_sold.split(',')
    # sale_goods_list = listify(object.goods_sold, str)
    battery_inv = [good for good in all_sale_inv if 'battery' in good.name.lower()]
    inverter_inv = [good for good in all_sale_inv if 'inverter' in good.name.lower() ]
    obj_batt_serials = object.battery_serials
    obj_invt_serials = object.inverter_serials

    if request.method == 'POST': 
        form = request.POST  
        # print('form:', form) 

        # Extract data from form 
        goods = '' 
        prices = '' 
        quantities = ''
        total = 0.00 
        quantity_serial_tally = True 

        bat_serials = {} 
        for bat in battery_inv: 
            bat_serials[bat.name] = form.get(f'{bat}_serials').strip()
            # print('check 1:', bat_serials)
        battery_serials = repr(bat_serials) 
        
        inv_serials = {}
        for invt in inverter_inv: 
            inv_serials[invt.name] = form.get(f'{invt}_serials').strip()
        inverter_serials = repr(inv_serials)

        for inv in all_sale_inv:
            try: 
                good_ = form.get(inv.name)
                price_ = form.get(inv.name + '_price')
                quantity_ = form.get(inv.name + '_quantity') 
                
                if good_ and float(price_) and int(quantity_):
                    goods += f'{inv.name},'  
                    # print(goods) 
                    prices += f'{price_},'
                    quantities += f'{quantity_},'
                    total += (float(price_) * int(quantity_))                
                    
            except (KeyError, TypeError, ValueError): 
                continue 

            try:
                quantity_ = form.get(inv.name + '_quantity') 
                if len(listify(bat_serials[inv.name], str)) > int(quantity_): 
                    quantity_serial_tally = False
            except (KeyError, AttributeError, ValueError): 
                pass 
        # print('check serial and quantities', quantity_serial_tally) 
        # print(bat_serials, inv_serials)

        goods = goods.removesuffix(',') 
        prices = prices.removesuffix(',') 
        quantities = quantities.removesuffix(',') 

        ##############################################
        ''' Refresh page if no goods selected '''
        # Re-render update page with error message if no goods were actually sold
        no_good_error = 'Please select one or more goods and enter correct prices and quantities'
        if (goods == '') or (not quantity_serial_tally):
            # print('Nothing sold in update')
            if not quantity_serial_tally:
                no_good_error = '**The serial numbers cannot be more than the quantities of goods sold**'
            # print(obj_batt_serials, obj_invt_serials)
            
            all_sale_quantities, obj_date, zipped = contextPrep(object, all_sale_inv, all_goods) 
            context = {
                'object': object, 
                'all_sale_inv': all_sale_inv, 
                'all_goods': all_goods, 
                'all_sale_quantities': all_sale_quantities, 
                'zipped': zipped, 
                'obj_date': obj_date, 
                'battery_inv': [inv.name for inv in battery_inv], 
                'inverter_inv': [inv.name for inv in inverter_inv], 
                'no_good_error': no_good_error,
                'obj_batt_serials': eval(obj_batt_serials), 
                'obj_invt_serials': eval(obj_invt_serials), 
            }
            return render(request, template_name, context) 
        #######################################3

        customer_name = form.get('customer_name') 
        customer_phone = form.get('customer_phone') 
        date = form.get('date') 
        if not date:
            date = theDate.today()
        details = form.get('details')

        #################################3
        ''' Obtain new and old quantities and goods values in order to update 
         inventory quantities '''
        old_goods_list = object.goods_sold.split(',') 
        for i, good in enumerate(old_goods_list[:]):
            old_goods_list[i] = good.strip()
        old_quantities_list = object.quantities.split(',') 
        # print('old', old_goods_list, old_quantities_list)
        new_goods_list = goods.split(',') 
        new_quantities_list = quantities.split(',') 
        # print('new', new_goods_list, new_quantities_list)
        ####################################################

        # Update object records with form values 
        object.goods_sold = goods 
        object.prices = prices 
        object.quantities = quantities 
        object.battery_serials = battery_serials
        object.inverter_serials = inverter_serials
        object.customer_name = customer_name 
        object.customer_phone = customer_phone 
        object.date = date 
        object.details = details 
        object.total = total 
        # # print(object.total)

        #####################################################333
        ''' Update Inventory '''
        # Get all inventory in order to loop over them and compare with sale inventory 
        # all_inv = Inventory.objects.all() 

        for inv in all_sale_inv:
            # if inventory name is in sale inventory,
            # get quantity difference between the updated and previous quantity values

            # Three possibilities: 
            # print('Updating inventory') 
            if inv.name in old_goods_list: 
                if inv.name in new_goods_list:
                    # 1. inv.name was in old_list and is also in new_list
                    ind = new_goods_list.index(inv.name)
                    new_quan = new_quantities_list[ind]
                    ind = old_goods_list.index(inv.name)
                    old_quan = old_quantities_list[ind]
                    # # print(inv.name, 'is in both lists', inv.quantity, old_quan, new_quan)
                    diff = int(old_quan) - int(new_quan)
                    inv.quantity += diff 
                else:
                    # 2. inv.naem was in old_list but is not in new_list
                    ind = old_goods_list.index(inv.name)
                    old_quan = old_quantities_list[ind]
                    # # print(inv.name, 'is only in old_list', inv.quantity, old_quan)
                    inv.quantity += int(old_quan) 
            elif inv.name in new_goods_list: 
                # 3. inv.name was not in old_list but is now in new_list 
                ind = new_goods_list.index(inv.name)
                new_quan = new_quantities_list[ind]
                # # print(inv.name, 'is only in new_list', inv.quantity, new_quan) 
                inv.quantity -= int(new_quan) 
            inv.save()

        ############################################################3

        # UPDATE REMINDERS 
        # if object is updated, check whether the date still matches the 
        # last refill date of the reminder. If not, delete the reminder, 
        # mark the object as having no reminder 
        object_refill_reminder = object.refillreminder_set.first()
        if object_refill_reminder: 
            if object.date != object_refill_reminder.last_refill_date:
                object_refill_reminder.delete()
                object.has_refill_reminder = False 

        # if object is updated, check whether the products and serial nums of the 
        # warranty reminders associated with the object are all still found 
        # in the objects serials records 
        object_warranty_reminders = object.warrantyreminder_set
        for rem in object_warranty_reminders.iterator():
            if (rem.product in object.goods_sold) and (rem.serial_no in object.battery_serials or rem.serial_no in object.inverter_serials): 
                pass
            else: 
                rem.delete()

        object.save() 

        return redirect('../')

    elif request.method == 'GET': 
        all_sale_quantities, obj_date, zipped = contextPrep(object, all_sale_inv, all_goods) 

        update_serial_list = []
        
        # print(inverter_inv) 

        context = {
            'object': object, 
            'all_sale_inv': all_sale_inv, 
            'all_goods': all_goods, 
            'all_sale_quantities': all_sale_quantities, 
            'zipped': zipped, 
            'obj_date': obj_date,
            'battery_inv': [inv.name for inv in battery_inv], 
            'inverter_inv': [inv.name for inv in inverter_inv], 
            'obj_batt_serials': eval(obj_batt_serials), 
            'obj_invt_serials': eval(obj_invt_serials), 
        }
        return render(request, template_name, context) 

def contextPrep(object, all_sale_inv, all_goods):
    '''
    This function prepares the context data for rendering a new page 
    ''' 
    all_quantities = object.quantities.split(',') 
        
    for i in range(len(all_quantities[:])):
        all_quantities[i] = int(all_quantities[i]) 

    all_sale_quantities = {}
    for i, good in enumerate(all_goods):
        good = good.strip()
        all_sale_quantities[good] = all_quantities[i] 
        # # print(good, all_sale_quantities) 
    # print('before get', all_goods, list(all_sale_quantities.keys()))
    dum = []
    for i in range(len(all_sale_inv)):
        if all_sale_inv[i].name in object.goods_sold:
            dum.append(all_sale_quantities[all_sale_inv[i].name])
            continue
        dum.append(None)

    # The date must be cast to a String before it can be set in the date input
    obj_date = str(object.date)

    # Better to find a way to zip the items to be used in a for loop
    zipped = zip(all_sale_inv, dum)
    return all_sale_quantities, obj_date, zipped

def saleDelete(request, id):
    template_name = 'sale/sale_confirm_delete.html' 
    object = Sale.objects.get(id=id) 
    context = {
        'object': object
    }
    return render(request, template_name, context)

class SaleConfirmDeleteView(View):
    template_name = 'sale/sale_confirm_delete.html' 
    success_url = '../../list' 

    def get_object(self):
        id_ = self.kwargs.get('id') 
        object = Sale.objects.get(id=id_) 
        return object

    def get(self, request, *args, **kwargs):
        object = self.get_object() 
        return render(request, self.template_name, {'object': object})

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        # Increase the quantities of invnetory in sale when the sale record is deleted 
        # Get names of inventory from sale, compare with sale inventory and 
            # update inventory quantities 
        goods = object.goods_sold.split(',') 
        quantities_list = object.quantities.split(',') 

        all_inv = Inventory.objects.filter(deactivate=False)
        for inv in all_inv:
            if inv.name in goods:
                ind = goods.index(inv.name) 
                quan = quantities_list[ind]
                inv.quantity += int(quan)
                inv.save()

        object.delete()
        return redirect('../../list') 