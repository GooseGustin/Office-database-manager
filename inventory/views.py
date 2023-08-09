from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, 
    DeleteView, 
    DetailView, 
    ListView,
    UpdateView)

from .forms import InventoryCreateForm, TypeCreateForm
from .models import Inventory, InventoryType


# Create your views here
class InventoryListView(ListView):
    # model = Inventory 
    template_name = 'inventory/inventory_list.html'
    queryset = Inventory.objects.all() 


class InventoryDetailView(DetailView):
    template_name = 'inventory/inventory_detail.html' 
    queryset = Inventory.objects.all()  # limits the list of objects to search in

    def get_object(self):
        pk_ = self.kwargs.get('pk') 
        object = Inventory.objects.get(pk=pk_) 
        # # # print(object.pk, object.id)
        return object 
        

class InventoryDeleteView(DeleteView):
    template_name = 'inventory/inventory_delete.html' 
    success_url = '../../list/'

    def get_object(self):
        pk_ = self.kwargs.get('pk') 
        object = Inventory.objects.get(pk=pk_) 
        return object 

def inventoryCreateView(request):
    '''I used a FBV instead of a CBV because I had to manually convert 
    some of the form data into models before saving the inventory object''' 
    no_good_error = ''
    if request.method == 'POST':
        type_name = request.POST.get('type') 
        type_object = InventoryType.objects.get(name=type_name) 
        name =  request.POST.get('name') 
        # # print(in_office, type(in_office)) 
        quantity =  request.POST.get('quantity') 
        found_in_office = request.POST.get('in_office') 
        in_office =  True if found_in_office=='on' else False 
        unit_price =  request.POST.get('unit_price') 
        warranty = request.POST.get('warranty_period') 
        if not warranty: 
            warranty = 0
        if quantity and name and unit_price:
            instance = Inventory.objects.create(
                    type=type_object, 
                    name=name, 
                    in_office=in_office, 
                    quantity=quantity, 
                    unit_price=unit_price, 
                    warranty_period=warranty, 
                )
            instance.save() 
            return redirect('../list/')
        else: 
            no_good_error = '''Please enter the valid item name, quantity and unit price''' 
        
    # elif request.method == 'GET': 
    form = InventoryCreateForm()
    all_types = InventoryType.objects.all() 
    context = {
        'form': form, 
        'all_types': all_types, 
        'no_good_error': no_good_error
    }
    return render(request, 'inventory/inventory_create.html', context)

def inventoryUpdateView(request, pk):
    '''Something interesting I did was the way I returned to the detail view
    for the object after creating it. In this case, I returned a redirect
    to the object's get_absolute_url method directly called and passed to 
    the fxn's 'to' argument
    ''' 
    # # print('Updating inventory')
    no_good_error = ''
    instance = Inventory.objects.get(pk=pk) 
    all_types = InventoryType.objects.all() 
    if request.method == 'POST': 
        form = InventoryCreateForm(request.POST)
        # # print('Form', form.data)

        instance.type = InventoryType.objects.get(name=form.data['type']) 
        instance.name = form.data['name'] 
        instance.quantity = form.data['quantity']  
        found_in_office = form.data.get('in_office', None) 
        instance.in_office =  True if found_in_office=='on' else False 
        instance.unit_price = form.data['unit_price'] 
        instance.warranty_period = form.data['warranty_period'] 
        deactivate = form.data.get('deactivate') 
        instance.deactivate = True if deactivate == 'on' else False 
        if instance.quantity and instance.unit_price:
            # # print('Valid form') 
            instance.save() 
            return redirect(to=instance.get_absolute_url())
        else:
            # # print('Invalid form', form.data)
            no_good_error = '''Please enter the valid item name, quantity and unit price''' 

    # elif request.method == 'GET': 
    # # print('Requesting the page') 
    form = InventoryCreateForm(instance=instance)
    context = {
        'form': form, 
        'object': instance, 
        'all_types': all_types, 
        'no_good_error': no_good_error
    }
    return render(request, 'inventory/inventory_update.html', context)

# def inventoryTypeCreateView(request, pk)
class InventoryTypeCreateView(CreateView):
    form_class = TypeCreateForm
    template_name = 'inventory/type_create.html' 
    queryset = InventoryType.objects.all()
    success_url = '../list/'