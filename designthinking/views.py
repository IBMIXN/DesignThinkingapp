import calendar

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from users.forms import UserUpdateForm, ProfileUpdateForm
from .forms import *
from .api import *
from .dbconnection import *
from .audio import *




@login_required
def profile(request):
    if request.method == 'POST':
        uForm = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        pForm = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if uForm.is_valid() and pForm.is_valid():
            uForm.save()
            pForm.save()
            messages.success(request, f'Account successfully updated')
            return redirect('profile')
    # return statement in line above is to prevent user from falling to line below
    # phenomenon called 'get-redirect pattern'- when u reload browser after submitting data
    # post request will be duplicated.
    else:
        uForm = UserUpdateForm(instance=request.user)
        pForm = ProfileUpdateForm(instance=request.user.profile)
    if request.session.get(request.user.email)!=None:
        project = request.session.get(request.user.email)
    else:
        projectID = getProjectID(request.user.email)
        project = getProjectName(projectID)
        request.session[request.user.email] = project
    context = {
        'uForm': uForm,
        'pForm': pForm,
        'projects': project,
    }
    return render(request, "designthinking/profile.html", context)


@login_required
def dashboard(request):
    if request.session.get(request.user.email)!=None:
        project = request.session.get(request.user.email)
    else:
        projectID = getProjectID(request.user.email)
        project = getProjectName(projectID)
        request.session[request.user.email] = project
    if request.method == 'POST':
        if request.POST.get('delete')!=None:
            delete_project = request.POST.get('delete')
            print(delete_project)
            deleteProject(request.user.email, delete_project)
            projectID = getProjectID(request.user.email)
            project = getProjectName(projectID)
            request.session[request.user.email] = project
    context = {
        'projects': project
    }
    return render(request, 'designthinking/dashboard.html', context)

@login_required
def newdesign(request):
    response = []

    # initiate the conversation with chatbot if no context stored in session
    if 'chatbot_context' not in request.session or request.session['chatbot_context'] == {}:
        chatbot_context = {}
        response, chatbot_context = getChatbotResponse('', chatbot_context)
        request.session['chatbot_context'] = chatbot_context
        for res in response:
                if res['response_type'] == 'text':
                    chatHistory = []
                    chatHistory.append({'robot_is_sender': True, 'text': res['text']})
                    print(res['text'])
                    speak(res['text'])
        request.session['chatHistory'] = chatHistory

    # if an user input is received
    if request.method == 'POST':
        # if the input is user's input in the chat
        if request.FILES.get('audio_data'):
            print("YESSSSSSSSSSSSSSSSS")
        else:
            print("NOOOOOOOOOOOOOOOOO")
        if request.POST.get("user_input")!= None and request.POST.get("user_input")!='':
            user_input = request.POST.get("user_input")
            chatHistory = request.session['chatHistory']
            chatHistory.append({'robot_is_sender': False, 'text': user_input})
            request.session['chatHistory'] = chatHistory
            chatbot_context = request.session['chatbot_context'] 
            response, chatbot_context = getChatbotResponse(user_input, chatbot_context)
            request.session['chatbot_context'] = chatbot_context
            for res in response:
                if res['response_type'] == 'text':
                    chatHistory = request.session['chatHistory']
                    chatHistory.append({'robot_is_sender': True, 'text': res['text']})
                    print(res['text'])
                    speak(res['text'])
            request.session['chatHistory'] = chatHistory
        # if the input is to sort the ideas list
        elif request.POST.get("sort")!=None:
            sort = request.POST.get("sort")
            print(sort)
    content = {}
    # check if we have received some contents from the users
    if request.session['chatbot_context']['skills']['main skill'].get('user_defined')!=None:
        content = request.session['chatbot_context']['skills']['main skill']['user_defined']

    # process the data in as is process for it to be better displayed on the page 
    if content.get('as_is_process')!=None:
        new_as_is = []
        for i in range (len(content['as_is_process'])):
            new_as_is.append({'order': str(i+1), 'text': content['as_is_process'][i]})
        content['as_is'] = new_as_is

    # process the data of ideas for it to be better displayed on the page 
    if content.get('ideas')!=None:
        new_ideas = []
        i = 0
        while i < (len(content['ideas'])):
            new_ideas.append({'text': content['ideas'][i], 'complexity': content['ideas'][i+1], 'expensive': content['ideas'][i+2]})
            i+=3
        content['new_ideas'] = new_ideas

    # We assign the id of each project by the user id of the chatbot because chatbot assign a unique id for each session
    content['id'] = request.session['chatbot_context']['global']['system']['user_id']


    # check what projects are in the user's account 
    # this is to be used in the hyperlink in review dropdown list
    if request.session.get(request.user.email)!=None:
        project = request.session.get(request.user.email)
    else:
        projectID = getProjectID(request.user.email)
        project = getProjectName(projectID)
        request.session[request.user.email] = project

    if content.get('save')!=None:
        if content['save'] == 'True':
            saveProject(request.user.email, content)
            request.session['chatbot_context']={}
            request.session[request.user.email].append({'id': content['id'], 'user': content['user'], 'name': content['project_name']})


    context = {
        'chathistory': request.session['chatHistory'],
        'messageNumber': len(request.session['chatHistory']),
        'content':content,
        'projects': project,
    }
    # print(request.session['chatbot_context'])
    # print(request.session['chatHistory'])
    # print(request.session['chatbot_context']['skills']['main skill'])
    return render(request, 'designthinking/newdesign.html', context)

@login_required
def review(request, id):
    projectID = getProjectID(request.user.email)
    project = getProjectName(projectID)
    if request.session.get(id):
        content = request.session.get(id)
    else:
        content = getProjectContent(id)
        request.session[id] = content
    if request.method == 'POST':
        # if request.POST.get('delete')!=None:
        #     if request.POST.get('name')!=None:
        if (request.POST.get('delete'))!=None:
            print(request.POST.get('delete'))
            sequence = request.POST.get('delete')
            table = request.POST.get('name')
            print(table)
            rows = content[table]
            for row in rows:
                if row['sequence'] == sequence:
                    item = row
            deleteItem(table,item)
        textToAdd = request.POST.get('add')
        if textToAdd!=None and textToAdd!='':
            
            table = request.POST.get('name')
            print(textToAdd)
            print(table)
            if "Empathy" in table:
                value = [id, textToAdd]
                insertSingleTwo(table, value)
            else:
                complexity = request.POST.get('complexity')
                expensive = request.POST.get('expensive')
                value = [id, complexity, expensive, textToAdd]
                insertSingleFour(table, value)
    if request.session.get(id):
        content = getProjectContent(id)
        request.session[id] = content
    else:
        content = getProjectContent(id)
        request.session[id] = content


    context = {
        'content':content,
        'projects': project,
    }
    return render(request, 'designthinking/review.html', context)


@login_required
def helpPage(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid:
            form.save()
            messages.success(request, f'Message sent!')
            send_mail(form.cleaned_data.get('subject'),
                      form.cleaned_data.get('message') + "\n\n Reply to: " + form.cleaned_data.get('email'),
                      'ixn.ibmdesignthinking@gmail.com', ['ixn.ibmdesignthinking@gmail.com'])
            return redirect('dashboard')
    else:
        form = ContactForm()
    context = {
        'form': form
    }
    return render(request, 'designthinking/help.html', context)



