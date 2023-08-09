from django.shortcuts import render, redirect
from django.core.exceptions import FieldError
from django.db.models import Q

from .models import RefillReminder, WarrantyReminder, MaintenanceReminder
from sale.models import Sale 
from job.models import Job 
from staff.models import Staff 
from inventory.models import Inventory 

from datetime import date
from datetime import datetime
from os import getlogin
import logging 
import xlsxwriter as xl 

logging.basicConfig(
    level=logging.ERROR, 
    encoding='utf-8'
)
logger = logging.getLogger()
debug = lambda text: logger.debug(text) 
info = lambda text: logger.info(text) 
warning = lambda text: logger.warning(text) 

# Create your views here.
ALL_STAFF = Staff.objects.all()
TODAY = date.today()
current_year = TODAY.year
ALL_YEARS = list(range(current_year-10, current_year+30))
MONTHS = [
        'January', 'February', 'March', 
        'April', 'May', 'June', 'July', 
        'August', 'September', 'October', 
        'November', 'December'
    ]
ALL_INVENTORY = Inventory.objects.filter(deactivate=False) 
ALL_SALES = Sale.objects.all() 
ALL_JOBS = Job.objects.all() 

# days_in_a_month = 30 

def homeView(request):
    context = {} 
    return render(request, 'core/home.html', context)

def helpView(request):
    context = {}
    return render(request, 'core/help.html', context)

def listify(obj_string, obj_type): 
    obj_list = []
    for obj_string_item in obj_string.split(','):
        if obj_string_item: 
            obj_list.append(obj_type(obj_string_item))
    return obj_list
    
def getCellName(row, col):
    r = row + 1
    c = chr(col + 65)
    cell_name = c + str(r) 
    return cell_name 

def exportReport(search_results): 
    '''
    Export the report, filtered or not, to an excel file saved in the Documents 
    folder on the computer 
    ''' 
    # # print('Exporting')
    monthly_sale_transactions = {}
    monthly_job_transactions = {}
    sales = search_results['monthly_sale_transactions']
    jobs = search_results['monthly_job_transactions'] 
    months = search_results['months'] if search_results['months'] else MONTHS
    
    # Match months to the sales and jobs completed in them 
    for month in MONTHS: 
        month_ind = MONTHS.index(month) + 1
        monthly_sale_transactions[month] = [
            *[sale for sale in sales if sale.date.month == month_ind], 
        ]
        monthly_job_transactions[month] = [
            *[job for job in jobs if job.date.month == month_ind]
        ]

    # # print(monthly_sale_transactions)
    # # print(monthly_job_transactions)

    username = getlogin()
    unique_ms = datetime.now().microsecond
    unique_id = f"{TODAY.day}{TODAY.month}{TODAY.year}_{unique_ms}"
    workbook = xl.Workbook(f"C:/Users/{username}/Documents/Report_{unique_id}.xlsx") 
    worksheet = workbook.add_worksheet()

    title_format = workbook.add_format({
            'bold': True, 
            # 'underline': True, 
            'align': 'center', 
            'font_size': 20})
    p1, p2 = getCellName(0,0), getCellName(0,14)
    worksheet.merge_range(f'{p1}:{p2}', 'Sales and Jobs Report', title_format)

    # Write sales report 
    sales_headings = [
        'Date', 'Good Sold', 'Unit Price', 'Quantity', 'Serial Numbers', 
        'Customer', 'Phone', 'Details'
    ]
    transaction_format = workbook.add_format({
            'bold': True, 
            'align': 'center', 
            'font_color': 'red', 
            'font_size': 16})
    month_format = workbook.add_format({
            'bold': True, 
            'font_color': 'blue'})
    bold_format = workbook.add_format({'bold': True})
    p1_sales, p2_sales = getCellName(1,0), getCellName(1,6)
    worksheet.merge_range(f'{p1_sales}:{p2_sales}', 'Sales', transaction_format)
    row = 2; col = 0
    for month in months: 
        if monthly_sale_transactions[month]:
            col = 0
            worksheet.write(row, col, month, month_format) 
            row += 1 
            # Headers
            for header in sales_headings:
                worksheet.write(row, col, header, bold_format)
                col += 1
            row += 1
            # For each sale 
            for sale in monthly_sale_transactions[month]:
                first_sale_row = row 
                col = 0
                goods = listify(sale.goods_sold, str) 
                prices = listify(sale.prices, float) 
                quantities = listify(sale.quantities, int) 
                # Date
                worksheet.write(row, col, str(sale.date))
                # 
                col += 1
                # Good sold, unit price, quantity 
                for i in range(len(goods)):
                    worksheet.write(row, col, goods[i]) # Good sold
                    worksheet.write(row, col+1, prices[i])  #  Unit price
                    worksheet.write(row, col+2, quantities[i])  # Quantiy
                    row += 1
                # Total 
                worksheet.write(row, col, 'Total', bold_format)
                worksheet.write(row, col+1, sale.total)
                
                last_sale_row = row
                row = first_sale_row
                # Serial numbers 
                col += 3
                batt_serials = eval(sale.battery_serials) 
                invt_serials = eval(sale.inverter_serials) 
                for good in goods: 
                    if good in batt_serials: 
                        worksheet.write(row, col, batt_serials[good])

                    if good in invt_serials: 
                        worksheet.write(row, col, invt_serials[good])
                    row += 1

                # Customer
                col += 1
                row = first_sale_row
                worksheet.write(row, col, sale.customer_name) # Customer
                col += 1
                worksheet.write(row, col, sale.customer_phone)    # Phone 
                col += 1
                worksheet.write(row, col, sale.details) # Details
                row = last_sale_row

                # Empty row
                row += 1
                worksheet.write(row, col, '')
        
            # Empty row
            row += 1
            worksheet.write(row, col, '')

    # Empty row
    row += 1
    worksheet.write(row, col, '')

    # Write job report 
    jobs_headings = [
        'Date', 'Inventory Used', 'Unit Price', 'Quantity', 
        'Serial Numbers', 'Extra Item', 'Extra Cost', 
        'Staff Assigned', 'Location', 'Status', 'Description',
        'Customer', 'Phone', 'Remark', 'Customer Fee'
    ]
    col = 0
    # # print('Job start', row, col) 
    p1_jobs, p2_jobs = getCellName(row,0), getCellName(row,14)
    worksheet.merge_range(f'{p1_jobs}:{p2_jobs}', 'Jobs', transaction_format)
    row += 1
    for month in months: 
        if monthly_job_transactions[month]:
            col = 0
            worksheet.write(row, col, month, month_format) 
            row += 1 
            # Headers
            for header in jobs_headings:
                worksheet.write(row, col, header, bold_format)
                col += 1
            row += 1
            # For each job 
            for job in monthly_job_transactions[month]:
                first_good_row = row 
                col = 0
                goods = listify(job.inventory_used, str) 
                prices = listify(job.prices, float) 
                quantities = listify(job.quantities, int) 
                other_items = listify(job.other_items, str)
                other_items.append('Transportation') 
                other_costs = listify(job.other_items_expenses, float) 
                other_costs.append(job.transportation_cost)
                staff_assigned = listify(job.staff_assigned, str)
                # Date
                worksheet.write(row, col, str(job.date))
                # 
                col += 1
                # # print('before goods', row, col)
                for i in range(len(goods)):
                    worksheet.write(row, col, goods[i]) # Good sold
                    worksheet.write(row, col+1, prices[i])  #  Unit price
                    worksheet.write(row, col+2, quantities[i])  # Quantiy
                    row += 1

                job_last_row = (first_good_row + max(len(goods), len(other_items), len(staff_assigned)) + 1)

                # # print('after goods', row, col) 
                last_good_row = row
                row = first_good_row

                # Serial numbers 
                col += 3
                batt_serials = eval(job.battery_serials) 
                invt_serials = eval(job.inverter_serials) 
                for good in goods: 
                    if good in batt_serials: 
                        worksheet.write(row, col, batt_serials[good])

                    if good in invt_serials: 
                        worksheet.write(row, col, invt_serials[good])
                    row += 1

                # Customer
                col += 1
                row = first_good_row
                # Extra items and costs
                for item, cost in zip(other_items, other_costs):
                    worksheet.write(row, col, item)
                    worksheet.write(row, col+1, cost) 
                    row += 1
                # Other Items 
                worksheet.write(job_last_row-1, col-3, 'Total', bold_format)
                worksheet.write(job_last_row-1, col-2, job.total_expenses)
                # # print(job_last_row, col-3, 'Total')
                # Staff Assigned 
                col += 2 
                row = first_good_row
                for i, staff in enumerate(staff_assigned): 
                    worksheet.write(row+i, col, staff)

                row = first_good_row
                col += 1
                worksheet.write(row, col, job.location.title()) # Location
                col += 1
                worksheet.write(row, col, job.job_status) # Status
                col += 1
                worksheet.write(row, col, job.job_description) # Description
                col += 1
                worksheet.write(row, col, job.customer_name.title()) # Customer
                col += 1
                worksheet.write(row, col, job.customer_phone)    # Phone 
                col += 1
                worksheet.write(row, col, job.remark) # Remark
                col += 1
                worksheet.write(row, col, job.customer_charge) # Fee
                
                # Empty row
                row = job_last_row 
                # row += 1
                # worksheet.write(row, col, '')
        
            # Empty row
            row += 1
            worksheet.write(row, col, '')



    # Write jobs report

    workbook.close()

def reportView(request, search=None):
    template_name = 'core/report.html' 
    months = MONTHS 

    # Order sales and jobs by month
    monthly_sale_transactions = {}
    monthly_job_transactions = {}
    sales = Sale.objects.all()
    jobs = Job.objects.all()

    # use search results
    if search: 
        months = search['months'] if search['months'] else MONTHS 
        sales = search['monthly_sale_transactions']
        jobs = search['monthly_job_transactions'] 

    # map transactions to months 
    for month in MONTHS: 
        month_ind = MONTHS.index(month) + 1
        monthly_sale_transactions[month] = [
            *[sale for sale in sales if sale.date.month == month_ind], 
        ]
        monthly_job_transactions[month] = [
            *[job for job in jobs if job.date.month == month_ind]
        ]

    context = {
        'months': months, 
        'monthly_sale_transactions': monthly_sale_transactions, 
        'monthly_job_transactions': monthly_job_transactions, 
        'search_results': search, 
        'all_staff': ALL_STAFF, 
        'all_years': ALL_YEARS, 
        'all_inventory': ALL_INVENTORY
    }
    return render(request, template_name, context)

def filterView(request):
    ''' 
    This view processes the filter parameters submitted from the report page 
    and creates the appropriate output queryset for the search 
    '''
    # # # print('In filter') 
    form = request.POST
    # # # print('Search:', form) 
    
    year = form.get('year')
    if year: year = None if year=='----' else int(year) 
    
    month = form.get('month')
    if month: month = int(month[5:])
    # # # print('Month:', month, len(month), type(month)) 

    staff_assigned = form.get('staff_assigned') 
    if staff_assigned: staff_assigned = None if staff_assigned=='----' else staff_assigned
    
    inv_sold = form.get('goods_sold') 
    if inv_sold: inv_sold=None if inv_sold=='----' else inv_sold 
    
    location = form.get('location') 

    transaction_type = form.get('transaction_type') 

    export = form.get('export')

    # # # print('Form: y', year, 'm', month, 's', staff_assigned, 'i', inv_sold, 't', transaction_type)

    search_results = {
        'monthly_sale_transactions': Sale.objects.all(), 
        'monthly_job_transactions': Job.objects.all(), 
        'months': [], 
        'export': export
    } 

    # transaction_type, year, month, goods_sold, staff_assigned
    # # print()
    if transaction_type == 'sale': 
        # search_results['monthly_sale_transactions'] = Sale.objects.all()
        search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].none()
    elif transaction_type == 'job':     
        # search_results['monthly_job_transactions'] = Job.objects.all() 
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].none()
    # # # print('check 1', search_results)

    if year: 
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].filter(date__year=year)
        search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].filter(date__year=year)
        # # # print('check 2', search_results)

    if month: 
        search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].filter(date__month=month)
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].filter(date__month=month)
        search_results['months'].append(MONTHS[month-1]) 
        # # # print('check 3', search_results)

    if inv_sold: 
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].filter(goods_sold__icontains=inv_sold) 
        search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].filter(inventory_used__icontains=inv_sold) 
        # # # print('check 4', search_results)

    if staff_assigned:
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].none()
        if search_results['monthly_job_transactions']:
            search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].filter(staff_assigned__icontains=staff_assigned)
     
    if location: 
        search_results['monthly_sale_transactions'] = search_results['monthly_sale_transactions'].none()
        search_results['monthly_job_transactions'] = search_results['monthly_job_transactions'].filter(location__icontains=location)

    # # # print('Results:', search_results)

    if export:
        exportReport(search_results)

    return reportView(request, search_results)

def getJobGoodsNames(job, good_name):
    try: 
        serials_dict = {}
        if good_name == 'battery' and job.battery_serials: 
            serials_dict = eval(job.battery_serials)             
            return list(serials_dict.keys())
        elif good_name == 'inverter' and job.inverter_serials: 
            serials_dict = eval(job.inverter_serials) 
            return list(serials_dict.keys())
        elif good_name == 'panel': 
            panel_list = []
            # # # print('getting job goods', job.inventory_used)
            for good in listify(job.inventory_used, str):
                if good_name in good.lower(): 
                    panel_list.append(good) 
            return panel_list 
    except SyntaxError: 
        pass 
    return 

def getSaleGoodsNames(sale, good_name):
    try: 
        serials_dict = {}
        if good_name == 'battery' and sale.battery_serials: 
            serials_dict = eval(sale.battery_serials) 
        elif good_name == 'inverter' and sale.inverter_serials: 
            serials_dict = eval(sale.inverter_serials) 
        return list(serials_dict.keys())
    except SyntaxError: 
        pass 
    return 

def reminderHandleView(request):
    # # print('Handling reminders')
    # update refill dates, maintenance dates of jobs 
    # disregard/forget warranty reminders of some serial numbers/some goods 
    # REFILL REMINDERS 
    form = request.POST 
    
    # print(form) 
    refill_reminders = RefillReminder.objects.filter(forget=False) 
    for rem in refill_reminders: 
        try: 
            forget_code = f'refill_forget_{rem.id}'
            val1 = form.get(forget_code)
            if val1: 
                rem.forget = True 
                # print('Forget refill reminder')
            handled_code = f'refill_handle_{rem.id}'
            val2 = form.get(handled_code) 
            if val2: 
                rem.alert = False 
                rem.last_refill_date = TODAY 
                # print('Update last refill date')
            rem.save()
        except Exception as E: 
            print(E) 
    
    # MAINTENANCE REMINDERS 
    maintenance_reminders = MaintenanceReminder.objects.filter(forget=False)
    for rem in maintenance_reminders:
        try: 
            forget_code = f'maintain_forget_{rem.id}'
            val1 = form.get(forget_code) 
            if val1: 
                rem.forget = True 
                # print('Forgetting maintenance') 
            handled_code = f'maintain_handle_{rem.id}' 
            val2 = form.get(handled_code) 
            if val2: 
                rem.alert = False 
                rem.last_maintenance_date = TODAY 
                # print('Update last maintenance date') 
            rem.save() 
        except Exception as E: 
            print(E) 

    # WARRANTY REMINDERS 
    # SALES 
    sale_warranty_reminders = WarrantyReminder.objects.filter(forget=False).exclude(sale=None).order_by('sale__date')
        
    for rem in sale_warranty_reminders: 
        forget_code = f'warranty_handle_{rem.id}' 
        val = form.get(forget_code) 
        if val: 
            rem.forget = True 
            # print('Forgetting warranty') 
            rem.save()

    # JOBS
    job_warranty_reminders = WarrantyReminder.objects.filter(forget=False).exclude(job=None).order_by('job__date')

    for rem in job_warranty_reminders: 
        forget_code = f'warranty_handle_{rem.id}' 
        val = form.get(forget_code) 
        if val: 
            rem.forget = True 
            # print('Forgetting warranty') 
            rem.save()
            
    return redirect('../reminders/')

def reminderCreateView(request):
    ALL_JOBS = Job.objects.all() 
    all_warranty_reminders_serials = [rem.serial_no for rem in WarrantyReminder.objects.all()]

    warranty_reminders = WarrantyReminder.objects.all()
    maintenence_reminders = MaintenanceReminder.objects.all()    
    if request.method == 'GET': 

        # OLD REFILL REMINDERS  
        refill_reminders = RefillReminder.objects.filter(forget=False) 
        for rem in refill_reminders: 
            # For reminders already created
            months_passed = round((TODAY - rem.last_refill_date).days/30) 
            refill_alert = True if months_passed>=6 else False 
            rem.alert = refill_alert
            rem.save()

        # NEW REFILL REMINDERS 
        for job in ALL_JOBS.filter(has_refill_reminder=False):            
            has_battery = getJobGoodsNames(job, 'battery') 
            # # print(job.date)
            # # print('Has_battery', has_battery) 
            months_passed = round((TODAY - job.date).days/30)
            #     If months_passed >= 6: 
            refill_alert = True if months_passed>=6 else False
            if has_battery and refill_alert: 
            #         create a refill reminder for the batteries used in this job
                refill_reminder = RefillReminder.objects.create(
                        job = job, 
                        last_refill_date=job.date, 
                        alert=refill_alert, 
                        months_passed=months_passed
                    )
                refill_reminder.save()
                job.has_refill_reminder = True 
                job.save()
        
        for sale in ALL_SALES.filter(has_refill_reminder=False): 
            has_battery = getSaleGoodsNames(sale, 'battery') 
            # # print(sale.date) 
            # # print('Sale has battery', has_battery) 
            months_passed = round((TODAY - sale.date).days/30)
            refill_alert = True if months_passed>=6 else False 
            if has_battery and refill_alert: 
                refill_reminder = RefillReminder.objects.create(
                    sale=sale, 
                    last_refill_date=sale.date, 
                    alert=refill_alert, 
                    months_passed=months_passed
                )
                refill_reminder.save() 
                sale.has_refill_reminder = True 
                sale.save()

        refill_reminders = RefillReminder.objects.filter(forget=False, alert=True).order_by('last_refill_date')

        # OLD MAINTENANCE REMINDERS  
        maintenance_reminders = MaintenanceReminder.objects.filter(forget=False) 
        for rem in maintenance_reminders: 
            # For reminders already created
            months_passed = round((TODAY - rem.last_maintenance_date).days/30) 
            maintenance_alert = True if months_passed>=12 else False 
            rem.alert = maintenance_alert
            rem.save()

        # NEW MAINTENANCE REMINDERS 
        for job in ALL_JOBS.filter(has_maintenance_reminder=False): 
            has_panel = getJobGoodsNames(job, 'panel') 
            # print(job.date, 'has panel', has_panel)
            months_passed = round((TODAY - job.date).days/30)
            maintenance_alert = True if months_passed >= 12 else False 
            if has_panel and maintenance_alert: 
                maintenence_reminder = MaintenanceReminder.objects.create(
                    job=job, 
                    alert=maintenance_alert, 
                    last_maintenance_date = job.date, 
                    months_passed = months_passed
                )
                maintenence_reminder.save() 
                job.has_maintenance_reminder = True 
                job.save()
                # # print('reminder created, job saved')
        maintenence_reminders = MaintenanceReminder.objects.filter(forget=False, alert=True).order_by('last_maintenance_date')
        # # print('check 1')

        # WARRANTY REMINDERS 
        warranty_periods = {inv.name:inv.warranty_period for inv in ALL_INVENTORY}
        # print('Warranty periods:', warranty_periods) 

        for sale in ALL_SALES: 
            warning(('Looking through', sale))
            # get serials of each battery
            has_battery = getSaleGoodsNames(sale, 'battery')
            has_inverter = getSaleGoodsNames(sale, 'inverter') 
            batt_serials = eval(sale.battery_serials) or None
            invt_serials = eval(sale.inverter_serials) or None 
            if not sale.has_refill_reminder: 
                last_date = sale.date 
            else: 
                pass 
            months_passed = round((TODAY - sale.date).days/30)
            # print(sale.date, months_passed)

            if not has_battery and not has_inverter: continue 

            warning([has_battery, has_inverter])
            for batt_name in has_battery: 
                alert = True if months_passed>=warranty_periods[batt_name] else False
                for batt_no in listify(batt_serials[batt_name], str): 
                    # create reminders if not already considered 
                    if not sale.battery_serials_done: 
                        sale.battery_serials_done = ''
                        sale.save()
                    if batt_no in sale.battery_serials_done: 
                        break 
                    elif alert: 
                        warranty_reminder = WarrantyReminder.objects.create(
                            serial_no=batt_no, 
                            product=batt_name, 
                            months_passed=months_passed, 
                            alert=alert, 
                            sale=sale
                        )
                        warranty_reminder.save()
                        sale.battery_serials_done += f'{batt_no},'
                        sale.save()

            for invt_name in has_inverter: 
                alert = True if months_passed>=warranty_periods[invt_name] else False
                for invt_no in listify(invt_serials[invt_name], str): 
                    # create reminders if not already considered 
                    if invt_no in sale.inverter_serials_done: 
                        break 
                    elif alert: 
                        warranty_reminder = WarrantyReminder.objects.create(
                            serial_no=invt_no, 
                            product=invt_name, 
                            months_passed=months_passed, 
                            alert=alert, 
                            sale=sale
                        )
                        warranty_reminder.save()
                        sale.inverter_serials_done += f'{invt_no},'
                        sale.save()
        
        sale_warranty_reminders = WarrantyReminder.objects.filter(forget=False, alert=True).exclude(sale=None).order_by('sale__date')

        # print('JOBS') 
        for job in ALL_JOBS: 
            warning(('Looking through job', job))
            # get serials of each battery
            has_battery = getJobGoodsNames(job, 'battery')
            has_inverter = getJobGoodsNames(job, 'inverter') 
            batt_serials = eval(job.battery_serials) or None
            invt_serials = eval(job.inverter_serials) or None 
            months_passed = round((TODAY - job.date).days/30)
            # print(job.date, months_passed)

            if not has_battery and not has_inverter: continue 

            warning([has_battery, has_inverter])
            for batt_name in has_battery: 
                alert = True if months_passed>=warranty_periods[batt_name] else False
                for batt_no in listify(batt_serials[batt_name], str): 
                    # create reminders if not already considered 
                    if batt_no in all_warranty_reminders_serials: 
                        break 
                    elif alert: 
                        warranty_reminder = WarrantyReminder.objects.create(
                            serial_no=batt_no, 
                            product=batt_name, 
                            months_passed=months_passed, 
                            alert=alert, 
                            job=job
                        )
                        warranty_reminder.save()
                        job.battery_serials_done += f'{batt_no},'
                        job.save()

            for invt_name in has_inverter: 
                alert = True if months_passed>=warranty_periods[invt_name] else False
                for invt_no in listify(invt_serials[invt_name], str): 
                    # create reminders if not already considered 
                    if invt_no in job.inverter_serials_done: 
                        break 
                    elif alert: 
                        warranty_reminder = WarrantyReminder.objects.create(
                            serial_no=invt_no, 
                            product=invt_name, 
                            months_passed=months_passed, 
                            alert=alert, 
                            job=job
                        )
                        warranty_reminder.save()
                        job.inverter_serials_done += f'{invt_no},'
                        job.save()
        
        job_warranty_reminders = WarrantyReminder.objects.filter(forget=False, alert=True).exclude(job=None).order_by('job__date')
        # warranty_reminders = WarrantyReminder.objects.all().order_by('months_passed')
            
        context = {
            # 'sales_list': sales_list, 
            'refill_reminders': refill_reminders, 
            # 'warranty_reminders': warranty_reminders, 
            'maintenance_reminders': maintenence_reminders, 
            'sale_warranty_reminders': sale_warranty_reminders, 
            'job_warranty_reminders': job_warranty_reminders, 
        } 

    elif request.method == 'POST': 
        context = {}
    return render(request, 'core/reminders.html', context)

