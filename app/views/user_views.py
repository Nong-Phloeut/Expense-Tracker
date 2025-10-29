from django.shortcuts import render

def user_management(request):
    return render(request, 'user_management/list.html')
