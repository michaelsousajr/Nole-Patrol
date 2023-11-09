'''
Description: This file contains the code for the views of the np_app.
Author(s): Michael Sousa, Brian Arango, Caitlin Marie Grimes
Last Modified Date: 1 November 2023
Assumptions: N/A
References: https://docs.djangoproject.com/en/4.2/topics/http/views/
            https://docs.djangoproject.com/en/4.2/ref/request-response/
'''
import os
from django.shortcuts import render
from .forms import EmailSearchForm, PasswordSearchForm
from .models import EmailFile, RegisteredUser
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect

from cryptography.hazmat.primitives.ciphers.aead import AESCCM

KEY = bytes.fromhex('59f055c39b5074dc7ea97abde24fc05a')
NONCE = bytes.fromhex('c2bad8b4a4536c8f0732e8c2be')
aesccm = AESCCM(KEY)

def set_password(password):
        """
        Encrypts the password and stores the ciphertext.
        """
        password = aesccm.encrypt(NONCE, password.encode(), None).hex()
        return password

'''
Function Name: index(request)
Description: This function contains the code to render the index.html page and
             process the user's email search query.
Parameters: request
Return Value: HTTPResponse
Author(s): Michael Sousa Jr., Caitlin Marie Grimes
Last Modified Date: 27 October 2023
Assumptions: N/A
References: https://docs.djangoproject.com/en/4.2/ref/request-response/
'''
def index(request):
    print("Request method:", request.method)  # Debugging statement
    
    if request.method == 'POST': 
        form = EmailSearchForm(request.POST)
        
        if form.is_valid():
            user_email = form.cleaned_data['email']
            print("User email:", user_email)  # Debugging statement

            # Use Django's ORM to search for the email in the database.
            matching_records = EmailFile.objects.filter(name=user_email)
            print("Matching records:", matching_records)  # Debugging statement

            # If the email is found in the database, extract the distinct sources.
            if matching_records.exists():
                sources = set(record.source for record in matching_records)
                # Render the search.html page with the results.
                return render(request, 'search.html', {'user_email': user_email, 'sources': sources})
            else: 
                print("No matching records for:", user_email)  # Debugging statement
                # Render the search.html page with the no_match flag set to True.
                return render(request, 'search.html', {'no_match': True})
        else:
            print("Form errors:", form.errors)  # Debugging statement

    else: 
        form = EmailSearchForm()
    
    return render(request, 'index.html', {'form': form})
            
def breaches_page(request):
    return render(request, 'breaches.html')
            
def about_page(request):
    return render(request, 'about.html')

'''
Function Name: notify_page(request)
Description: This function handles the process of notifying users if their email is found in the breached 
             database. On a POST request, it checks the EmailFile model for the provided email. If found,
             it sends a breach notification to the user's email. Additionally, the email is saved in the
             RegisteredUser model if not already present. After processing, it redirects to a success page.
             It also sends a thank you email as a confirmation, useful for testing purposes.
Parameters: request
Return Value: HTTPResponse
Author(s): Brian Arango
Last Modified Date: 30 October 2023
Assumptions: The EmailFile model contains emails from breached databases. The RegisteredUser model saves 
             users who have been notified.
References: https://docs.djangoproject.com/en/4.2/ref/request-response/, 
            https://docs.djangoproject.com/en/4.2/topics/email/#
'''
def notify_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the email exists in the EmailFile model.
        exists_in_breach = EmailFile.objects.filter(name=email).exists()
        
        # If it exists in the breach, send a notification email to the user.
        breach_message = 'Your email has been found in our database of breached emails.\n' + \
                         'For a full list of past breaches affecting your email address, ' + \
                         'please see our database. We will notify you if your email is found in any future breaches.'
        if exists_in_breach:
            send_mail(
                'Breach Notification',
                breach_message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        
        # Save the email in the RegisteredUser model if it's not already there.
        created = RegisteredUser.objects.get_or_create(email=email)
        
        # If the user is newly registered (i.e., email was just added), send a thank you email.
        if created:
            send_mail(
                'Thank you for registering for Nole Patrol breach notifications',
                'Thank you for registering for email breach notifications. We will notify you if your email is found in any future breaches.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        
        # Redirect to a success page or display a success message (based on your design).
        return HttpResponseRedirect('/success/')  # Change this URL based on your design.

    return render(request, 'notify.html')
 
def success_view(request):
    return render(request, 'success.html')

'''
Function Name: index(request)
Description: This function contains the code to render the index.html page and
             process the user's email search query.
Parameters: request
Return Value: HTTPResponse
Author(s): Michael Sousa Jr., Caitlin Marie Grimes
Last Modified Date: 1 October 2023
Assumptions: N/A
References: https://docs.djangoproject.com/en/4.2/ref/request-response/
'''
def check_password(request):
    print("Request method:", request.method)  # Debugging statement
    print("Request data:", request.POST)  # Debugging statement
    
    if request.method == 'POST': 
        form = PasswordSearchForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            print("Password:", password)  # Debugging statement
            # Use Django's ORM to search for the password in the database.
            password=set_password(password)
            print("Encrypted Password:", password)
            matching_records = EmailFile.objects.filter(password=password)
            print(matching_records)
            #for record in matching_records:
            #    record.password = EmailFile.check_password(encrypted_password=record.password)
            #print("Matching records:", matching_records)  # Debugging statement

            # If the password is found in the database, extract the distinct sources.
            if matching_records.exists():
                sources = set(record.source for record in matching_records)
                # Render the search.html page with the results.
                return render(request, 'search.html', {'password': password, 'sources': sources})
            else: 
                print("No matching records for:", password)  # Debugging statement
                # Render the search.html page with the no_match flag set to True.
                return render(request, 'search.html', {'no_match': True})
        else:
            print("Form errors:", form.errors)  # Debugging statement

    else: 
        form = PasswordSearchForm()
    
    return render(request, 'checkpassword.html', {'form': form})
