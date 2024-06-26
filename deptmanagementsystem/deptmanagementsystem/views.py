from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Complaints, Forum, Marks, Student, User
from .forms import CommentForm, ForumForm, MarksForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import logout

import cv2
from pyzbar.pyzbar import decode
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
import base64
from PIL import Image
from io import BytesIO

def login_view(request):
    if(request.method == 'POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print("partially success" + "\n\n")
        if user is not None:
             print("success")
             login(request, user)
             return redirect(view_home)
        
    return render(request, 'login.html') 


def decode_barcodes(image_path):
    image = cv2.imread(image_path)
    barcodes = decode(image)

    if not barcodes:
        return redirect(login_view)
    
    for barcode in barcodes:
        return barcode.data.decode('utf-8')
        

def submit_image(request):
    if request.method == 'POST':
        image_data = request.POST.get('imageData')
        if image_data:
            # Remove the data:image/png;base64, part
            image_data = image_data.split(',')[1]
            image_data = base64.b64decode(image_data)

            image = Image.open(BytesIO(image_data))
            image.save('captured_image.png')

            barcodeData = decode_barcodes('captured_image.png')

            print(barcodeData)

            temp = barcodeData.split('-', 1)
            username = temp[0]
            password = temp[1]
          
            user = authenticate(request, username=username, password=password)
        print("partially success" + "\n\n")
        if user is not None:
             print("success")
             login(request, user)
             return redirect(view_home)

            # return HttpResponse(barcodeData)

    return render(request, 'login.html')

def view_home(request):
    student_name = request.user.username
    return render(request, 'home.html',{'student_name' : student_name})


def forum_view(request):
    if(request.method == 'POST'):
        form = ForumForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse('error')
        return redirect(forum_view)
    else:
        forums = Forum.objects.all()
        form = ForumForm()
        return render(request, 'forum.html', {'forums': forums, 'form' : form})

def forum_list(request):
    forums = Forum.objects.all()
    return render(request, 'forum_list.html', {'forums' : forums})

def forum_details(request, forum_id):
     print("title reached to function " +   str(forum_id))
     forum = get_object_or_404(Forum, pk=forum_id)
     form = CommentForm()
     return render(request, 'forum_details.html', {'forum' : forum , 'form' : form})

def submit_comment(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.cleaned_data['new_comment']
            forum.add_comment(new_comment)
            return redirect('forum-details', forum_id=forum_id )
        
    return redirect('forum-details', forum_id=forum_id)

def add_marks(request):
    students = Student.objects.all()
    marks = Marks.objects.all()
    if request.method == 'POST':
        for student in students:
            marks_value = request.POST.get(f"marks_{student.id}")
            if marks_value is not None:
                # Convert the input data to a floating-point number
                marks_value_float = float(marks_value)
                marks, created = Marks.objects.get_or_create(student=student)
                marks.cgp = marks_value_float  # Assign the floating-point value
                marks.save()
        return redirect('view-marks')
    return render(request, 'add_marks.html', {'students': students, 'marks' : marks})

def view_marks(request):

    if request.user.userType != 'stud' :
        marks_details = Marks.objects.all()
        return render(request, 'view_marks.html', {'marks_details' : marks_details})
    else:
        student = Student.objects.get(name = request.user.username)
        marks_details = Marks.objects.get(student = student)
        return render(request, 'view_marks.html', {'marks_details' : marks_details})

def add_forum(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('forum-list')
    else:
        form = ForumForm()
    return render(request, 'add_forum.html', {'form': form})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # semester = request.POST.get('semester')
            # batch = request.POST.get('batchNo')
            # batchId = f"{batch}{semester}"
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            student = Student(name=name, description=description)
            student.save()
            obj = Marks(student=student)
            obj.save()
            user = User.objects.create_user(username = name, email='', password=name, userType="stud")
            user.save()
            return redirect('view-student')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})


def view_student(request):
    student_details = Student.objects.all()
    return render(request, 'view_student.html', {'students' : student_details})


def add_complaint(request):
    if request.method == 'POST':
        print('working till here\n\n\n')
        subject = request.POST.get('subject')
        complaint_text = request.POST.get('complaintText')
        complaint = Complaints(subject=subject, description=complaint_text, user=request.user)
        complaint.save()
        return redirect('add-complaint')
    all_complaints = Complaints.objects.all()
    return render(request, 'complaintforum.html', {'complaints' : all_complaints})

def complaint_details(request, complaint_id):
    complaint = get_object_or_404(Complaints, pk=complaint_id)
    return render(request, 'complaintdetails.html', {'complaint': complaint})

def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaints, pk=complaint_id)
    complaint.delete()
    return redirect('add-complaint') 


def logout_view(request):
    logout(request)
    return redirect('login_view')

def test(request):
    return HttpResponse('success')


def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    user = get_object_or_404(User,username = student.name)
    marks = get_object_or_404(Marks,student = student)
    if request.method == 'POST':
        student.delete()
        user.delete()
        marks.delete()
        return redirect('view-student') 
    return redirect('view-student')

from django.shortcuts import render
from .forms import UserForm

def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            email = cleaned_data['email']
            password = cleaned_data['password']
            userType = cleaned_data['userType']

            print("\n\n\-----")
            print(userType)
            user = User.objects.create_user(username = username, email=email, password=password, userType=userType)
            user.save()
            return redirect('user-list')
    else:
        form = UserForm()
    return render(request, 'register_admin.html', {'form': form})


def view_users(request):
    # Query users whose userType is not 'student'
    users = User.objects.filter(userType__in=['prof', 'hod', 'clerk'])

    # Pass the users queryset to the template for rendering
    return render(request, 'user_list.html', {'users': users})


def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user-list')  # Redirect to the user list page after deletion
    return redirect('user-list')