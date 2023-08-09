from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView, 
    DetailView, 
    ListView, 
    UpdateView, 
    DeleteView
)
from .models import Staff 
from .forms import StaffCreateForm

# Create your views here
class StaffListView(ListView):
    # model = Staff 
    template_name = 'staff/staff_list.html'
    queryset = Staff.objects.all() 

def staffListView(request):
    context = {
        'object_list': Staff.objects.all()
    }
    return render(request, 'staff/staff_list.html', context) 

class StaffDetailView(DetailView):
    template_name = 'staff/staff_detail.html' 
    queryset = Staff.objects.all()  # limits the list of objects to search in


class StaffDeleteView(DeleteView):
    template_name = 'staff/staff_delete.html' 
    success_url = '../../list/'

    def get_object(self):
        pk_ = self.kwargs.get('pk') 
        object = Staff.objects.get(pk=pk_) 
        return object 

def correctDateString(date_string):
    parts = date_string.split('-') 
    day = parts[0] 
    month = parts[1]
    year = parts[2]
    correct_date_string = '-'.join((day, month, year)) 
    return correct_date_string

def staffCreateView(request):
    ''' I couldn't use a normal CBV because I had to convert some of the 
    form data into other models in order to save them. 
    Update: I didn't then know how to use generic CBVs. Check out sale app '''
    template_name = 'staff/staff_create.html'

    if request.method == 'POST':
        default_date = '1800-08-08'
        data = {}
        data['name'] = request.POST.get('name')
        data['date_of_leave'] = request.POST.get('date_of_leave') or default_date
        if data['date_of_leave'] != default_date: 
            data['has_left'] = True 
        else: data['has_left'] = False 
        data['phone'] = request.POST.get('phone') 
        data['email'] = request.POST.get('email') 
        data['state_of_origin'] = request.POST.get('state_of_origin')
        data['home_residence'] = request.POST.get('home_residence') 
        data['date_of_employment'] = request.POST.get('date_of_employment') or default_date
        if data['date_of_employment'] != default_date: 
            data['is_employed'] = True 
        else: data['is_employed'] = False 
        data['active'] = True if request.POST.get('active')=='on' else False

        # # # print('Creating staff', data) 

        if data['name'] and data['phone']:
            instance = Staff(**data) 
            instance.save() 
            return redirect('../list/')
        else: 
            # # # # print('Unsuccessful submission') 
            context = {
                'object': object, 
                'no_good_error': '** Name and phone number are required **', 
            }
            return render(request, template_name, context)
        
    elif request.method == 'GET': 
        form = StaffCreateForm()
        all_staff = Staff.objects.all()
        context = {
            'form': form, 
            'all_staff': all_staff
        }
        return render(request, template_name, context)


class StaffUpdateView(UpdateView):
    template_name = 'staff/staff_update.html' 
    form_class = StaffCreateForm
    queryset = Staff.objects.all() 
    # success_url = '../../list/'

    def get_object(self):
        pk_ = self.kwargs.get('pk') 
        object = Staff.objects.get(pk=pk_) 
        return object 

    def get_context_data(self, **kwargs):
        object = self.get_object() 
        context = super().get_context_data(**kwargs)
        context['date_of_leave'] = str(object.date_of_leave)
        context['date_of_employment'] = str(object.date_of_employment)
        return context 

    def post(self, request, *args, **kwargs):
        # # # print(request.POST)
        default_date = '1800-08-08'
        object = self.get_object() 
        data = {}
        data['name'] = request.POST.get('name')
        data['date_of_leave'] = request.POST.get('date_of_leave') or default_date
        if data['date_of_leave'] != default_date: 
            data['has_left'] = True 
        else: 
            data['has_left'] = False 
        data['phone'] = request.POST.get('phone') 
        data['email'] = request.POST.get('email') 
        data['state_of_origin'] = request.POST.get('state_of_origin')
        data['home_residence'] = request.POST.get('home_residence') 
        data['date_of_employment'] = request.POST.get('date_of_employment') or default_date
        if data['date_of_employment'] != default_date: 
            data['is_employed'] = True 
        else: 
            data['is_employed'] = False 
        data['active'] = True if request.POST.get('active')=='on' else False

        if data['name'] and data['phone']:
            # # # print('Successful submission')
            # # # print(data)
            Staff.objects.filter(id=object.id).update(**data) 
            # # print('check 1')
            return redirect('../')

        else: 
            # # # print('Unsuccessful submission') 
            dob = str(object.date_of_leave)
            doe = str(object.date_of_employment) 
            context = {
                'object': object, 
                'no_good_error': '** Name and phone number are required **', 
                'date_of_leave': dob, 
                'date_of_employment': doe, 
            }
            return render(request, self.template_name, context)

    def get(self, request, *args,**kwargs):
        object = self.get_object() 
        dob = str(object.date_of_leave)
        doe = str(object.date_of_employment) 
        context = {
            'object': object, 
            'date_of_leave': dob, 
            'date_of_employment': doe, 
        }
        return render(request, self.template_name, context)
