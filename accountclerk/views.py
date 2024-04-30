from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import auth
from manager.models import BalanceSheet
from shows.models import Shows
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.contrib import messages

@login_required
def accountclerk_dashboard(request):
      return render(request, 'accounts_dashboard.html')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required
def accounts_profile(request):
    
    account_clerk = request.user
    if request.method == 'POST':
        if(request.user.user_type!=2):
            auth.logout(request)
            return redirect('login')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        new_name = request.POST.get('name')
        
        # Check if passwords match
        if new_password != confirm_password:
            return render(request, 'accounts_profile.html', {'accounts': account_clerk, 'error': 'Passwords do not match'})
        
        # Update password if changed
        if new_password:
            account_clerk.password = new_password

        # Update name if changed
        if new_name:
            account_clerk.first_name = new_name
        
        account_clerk.full_clean()
        account_clerk.save()

        messages.error(request, 'Update Request Successful.')
        return redirect('accounts_profile')

    context = {'accounts': account_clerk}
    return render(request, 'accounts_profile.html', context)

@login_required
def add_expenses(request):
    if(request.user.user_type!=2):
            auth.logout(request)
            return redirect('login')
    if request.method == 'POST':
        expense_type = request.POST.get('expense_type')
        amount = request.POST.get('amount')
        show_id = request.POST.get('show_id')

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid amount. Please enter a positive number.')
            return redirect('add_expenses')

        # Retrieve the selected show
        try:
            selected_show = Shows.objects.get(pk=show_id)
        except Shows.DoesNotExist:
            messages.error(request, 'Selected show does not exist.')
            return redirect('add_expenses')

        # Save expense to BalanceSheet table
        BalanceSheet.objects.create(
            date=date.today(),
            amount=-amount, 
            type=expense_type,
            show_id=show_id 
        )

        messages.success(request, 'Expense added successfully.')
        return redirect('add_expenses')

    # Get all shows to display in the form
    shows = Shows.objects.all()
    return render(request, 'add_expenses.html', {'shows': shows})

@login_required
def view_expenses(request):
    if(request.user.user_type!=2):
            auth.logout(request)
            return redirect('login')
    
    expenses = BalanceSheet.objects.filter(sales_id=None)
    for expense in expenses:
      expense.amount = abs(expense.amount)
    return render(request, 'view_expenses.html', {'expenses': expenses})

@login_required
def edit_expense(request, txn_id):
    if(request.user.user_type!=2):
            auth.logout(request)
            return redirect('login')
    
    expense = get_object_or_404(BalanceSheet, txn_id=txn_id)

    if request.method == 'POST':

        expense_type = request.POST.get('expense_type')
        amount = request.POST.get('amount')
        show_id = request.POST.get('show_id')

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid amount. Please enter a positive number.')
            return redirect('edit_expense', txn_id=txn_id)

        # Retrieve the selected show
        try:
            selected_show = Shows.objects.get(pk=show_id)
        except Shows.DoesNotExist:
            messages.error(request, 'Selected show does not exist.')
            return redirect('edit_expense', txn_id=txn_id)

        # Update expense details
        expense.date = selected_show.date
        expense.amount = -amount  
        expense.type = expense_type
        expense.show_id = show_id  
        expense.save()

        messages.success(request, 'Expense updated successfully.')
        return redirect('view_expenses')

    shows = Shows.objects.all()
    expense.amount = abs(expense.amount)
    return render(request, 'edit_expense.html', {'shows': shows, 'expense': expense})

@login_required
def delete_expense(request, txn_id):
    if(request.user.user_type!=2):
            auth.logout(request)
            return redirect('login')
    
    expense = get_object_or_404(BalanceSheet, txn_id=txn_id)

    expense.delete()

    messages.success(request, 'Expense deleted successfully.')

    return redirect('view_expenses')