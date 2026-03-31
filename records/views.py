import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import JSONUploadForm
from .models import Record

def upload_view(request):
    form = JSONUploadForm()

    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                data = json.load(file)
            except (json.JSONDecodeError, UnicodeDecodeError):
                messages.error(request, 'File is not valid JSON')
                return render(request, 'records/upload.html', {'form': form})
            
            if not isinstance(data, list):
                messages.error(request, 'JSON must be an array of objects')
                return render(request, 'records/upload.html', {'form': form})
            
            errors = []
            records = []

            for i, item in enumerate(data, start=1):
                #check for name and data keys
                if 'name' not in item:
                    errors.append(f'Record {i}: no "name" field')
                    continue
                if 'date' not in item:
                    errors.append(f'Record {i}: no "date" field')
                    continue

                name = item['name']
                date = item['date']

                #name validation
                if len(name) >= 50:
                    errors.append(f'Record {i}: "name" field must be less than 50 chars')
                    continue
                #date validation
                try:
                    parsed_date = datetime.strptime(date, '%Y-%m-%d_%H:%M')
                except (ValueError, TypeError):
                    errors.append(f'Record {i}: "date" field wrong format (excepted -> YYYY-MM-DD_HH:mm)')
                    continue

                records.append(Record(name=name, date=parsed_date))

            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'records/upload.html', {'form': form})
            
            #if no errors -> save
            Record.objects.bulk_create(records)
            messages.success(request, f'Hurray! Succesfully loaded {len(records)} records!')
            return redirect('records:list')
        
    return render(request, 'records/upload.html', {'form': form})

def list_view(request):
    records = Record.objects.all()
    return render(request, 'records/list.html', {'records': records})