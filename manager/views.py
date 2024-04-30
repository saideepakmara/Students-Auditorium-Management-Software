from django.shortcuts import render,redirect
from .models import Users, BalanceSheet 
from shows.models import Shows
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from datetime import datetime
from django.contrib import messages

@login_required
def dashboard(request):
    manager_id = request.user.first_name
    return render(request, 'dashboard.html', {'manager_id': manager_id})

@login_required
def manager_profile(request):
    if(request.user.user_type!=1):
            auth.logout(request)
            return redirect('login')
    try:
        manager = Users.objects.get(username=request.user)
    except Users.DoesNotExist:
        return redirect('login')  

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        new_name = request.POST.get('name')
        
        # Check if passwords match
        if new_password != confirm_password:
            return render(request, 'manager_profile.html', {'manager': manager, 'error': 'Passwords do not match'})
        
        # Update password if changed
        if new_password:
            manager.password = new_password

        # Update name if changed
        if new_name:
            manager.first_name = new_name
        
        manager.save()

        return redirect('manager_profile')

    context = {'manager': manager}
    return render(request, 'manager_profile.html', context)

@login_required
def view_balance_sheet(request):
    if(request.user.user_type!=1):
            auth.logout(request)
            return redirect('login')
    
    if request.method == 'POST':
        show_id = request.POST.get('show')

        if not show_id:
            messages.error(request, 'Please select a show.')
            return redirect('view_balance_sheet')

        balance_sheet = BalanceSheet.objects.filter(show_id=show_id)

        curr_show = Shows.objects.get(show_id=show_id)

        total_amount = balance_sheet.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        # Calculate amount collected
        amount_collected = balance_sheet.exclude(sales_id=0).aggregate(amount_collected=Sum('amount'))['amount_collected'] or 0

        # Calculate expenditure
        expenditure = total_amount-amount_collected

        # Calculate net amount
        net_amount = amount_collected + expenditure

        shows = Shows.objects.all()

        context = {
            'balance_sheet': balance_sheet,
            'shows': shows,
            'amount_collected': amount_collected,
            'expenditure': expenditure,
            'net_amount': net_amount,
            'curr_show': curr_show
        }
        return render(request, 'view_balance_sheet.html', context)

    # Initial render with empty form
    shows = Shows.objects.all()
    context = {
        'shows': shows,
    }
    return render(request, 'view_balance_sheet.html', context)

@login_required
def yearly_balance_sheet(request):
    if(request.user.user_type!=1):
            auth.logout(request)
            return redirect('login')
    
    balance_sheet = None
    total_amount = 0
    years_list = []
    year=0
    amount_collected = 0
    expenditure = total_amount-amount_collected
    net_amount = amount_collected + expenditure

    if request.method == 'POST':
        year = request.POST.get('year')

        if not year:
            messages.error(request, 'Please select the year.')
            return redirect('yearly_balance_sheet')

        try:
            year = int(year)
        except ValueError:
            messages.error(request, 'Please select a valid year')
            return redirect('yearly_balance_sheet')
            pass
        else:
            balance_sheet = BalanceSheet.objects.filter(date__year=year)
            if balance_sheet.exists():
                total_amount = balance_sheet.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

                amount_collected = balance_sheet.exclude(sales_id=0).aggregate(amount_collected=Sum('amount'))['amount_collected'] or 0

                expenditure = total_amount-amount_collected

                net_amount = amount_collected + expenditure

    # Get unique years for the dropdown
    current_year = datetime.now().year
    years_list = list(range(current_year, current_year - 10, -1))  # Adjust the range as needed

    context = {
        'balance_sheet': balance_sheet,
        'years': years_list,
        'total_amount': total_amount,
        'expenditure': expenditure,
        'amount_collected': amount_collected,
        'net_amount': net_amount,
        'curr_year': year
    }
    return render(request, 'yearly_balance_sheet.html', context)

@login_required
def add_salesperson(request):
    if(request.user.user_type!=1):
            auth.logout(request)
            return redirect('login')
    
    manager_id = request.user.username 
    if request.method == 'POST':
        sales_id = request.POST.get('sales_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('name')

        if not sales_id:
            messages.error(request, 'Please Enter a sales ID.')
            return redirect('add_salesperson')
        
        if not username:
            messages.error(request, 'Please Enter a username.')
            return redirect('add_salesperson')
        
        if not password:
            messages.error(request, 'Please Enter a password.')
            return redirect('add_salesperson')
        
        if not first_name:
            messages.error(request, 'Please Enter a name.')
            return redirect('add_salesperson')
        
        salesperson = Users(sales_id=sales_id, username=username, password=password, first_name=first_name)
        salesperson.save()
        
        return redirect('salesperson_list')  
    
    return render(request, 'add_salesperson.html', {'manager_id': manager_id})

@login_required
def salesperson_list(request):
    if(request.user.user_type!=1):
            auth.logout(request)
            return redirect('login')
    manager_id = request.user.username 
    salespersons = Users.objects.filter(~Q(sales_id=0))
    return render(request, 'salesperson_list.html', {'salespersons': salespersons, 'manager_id': manager_id})

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

