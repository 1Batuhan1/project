from django.shortcuts import render


# Create your views here.

def index(request):
      
    meetups = [
       {
           'title' : 'A First Meet', 
           'Location': 'Usa', 
           'slug': 'a-first-meetup'    
        },
       {
           'title' : 'A Second Meet', 
           'Location': 'Norway', 
           'slug': 'a-second-meetup'
        }
    ]

    return render(request,'meetups/index.html',{
        'show_meetups':True,
        'meetups':meetups
        })

def meetup_details(request):
     
    selected_meetups = {
        'title': 'A first meetup', 
        'Description': 'This is the first meetup!'
                        }

    return render(request,'meetups/meetup-detail.html',{
        'meetup_title': selected_meetups['title' ],
        'meetup_description': selected_meetups['Description']
    })