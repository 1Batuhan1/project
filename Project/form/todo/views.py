from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from .models import todo

# Create your views here.

def base(request):
    users = todo.objects.all()  

    return render(request,"base.html",{"users":users})

def adduser(request):

    if request.method == "GET":

        return redirect("/")
     
    else:
     name = request.POST.get("name")
   
     surname = request.POST.get("surname")
  
     age = request.POST.get("age")
          
    newuser=todo(name=name,surname=surname,age=age)
       
    newuser.save()
    return redirect("/")
     
     
        
      
           
        
    



    
 
#def update(request,id):

    Todo = get_object_or_404(todo,id=id)

    

    Todo.save()
    return redirect("/")      

def delete(request,id):
    
    Todo = get_object_or_404(todo,id=id)
     
    Todo.delete()

    return redirect("/")
