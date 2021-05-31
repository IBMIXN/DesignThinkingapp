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


def sortByKey(ideas, key):
    if key == 'default':
        return ideas
    else:
        return sorted(ideas, key=lambda k: k[key]) 


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
    # check if the list of projects stored in the account is saved in session
    # if not, ask dbconnection.py for the list and store it in session
    # so views do not need to ask the database again when page is reloaded
    if request.session.get(request.user.email)!=None:
        project = request.session.get(request.user.email)
    else:
        projectID = getProjectID(request.user.email)
        project = getProjectName(projectID)
        request.session[request.user.email] = project

    # if a user delete a whole project from the dashboard 
    if request.method == 'POST':
        if request.POST.get('delete')!=None:
            delete_project = request.POST.get('delete')
            deleteProject(request.user.email, delete_project)
            projectID = getProjectID(request.user.email)
            project = getProjectName(projectID)
            request.session[request.user.email] = project

    # display the list of project IDs and project names
    context = {
        'projects': project
    }
    return render(request, 'designthinking/dashboard.html', context)

@login_required
def newdesign(request):
    # response stores the text response from Watson Assistant for the current turn
    # so it is always set to empty after a turn
    response = []

    # when page is loaded for the first time, set sorting algo to default
    if 'sort' not in request.session:
        request.session['sort'] = 'default'

    # initiate the conversation with chatbot if no context stored in session
    if 'chatbot_context' not in request.session or request.session['chatbot_context'] == {}:
        chatbot_context = {}
        response, chatbot_context = getChatbotResponse('', chatbot_context)
        # always store the context returned by Watson Assistant so that the states of conversation can be kept 
        request.session['chatbot_context'] = chatbot_context
        for res in response:
                if res['response_type'] == 'text':
                    chatHistory = []
                    chatHistory.append({'robot_is_sender': True, 'text': res['text']})
                    speak(res['text'])
        request.session['chatHistory'] = chatHistory

    # if an user input is received
    if request.method == 'POST':
        # if the input is user's input in the chat
        # empty input creates meaningless conversation and maybe caused by reloading the page 
        # so it should be ignored
        if request.POST.get("user_input")!= None and request.POST.get("user_input")!='':
            # Watson Assistant does not allow these three characters in input
            user_input = request.POST.get("user_input").replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            chatHistory = request.session['chatHistory']
            # This is for the display of chat history
            chatHistory.append({'robot_is_sender': False, 'text': user_input})
            chatbot_context = request.session['chatbot_context'] 
            response, chatbot_context = getChatbotResponse(user_input, chatbot_context)
            request.session['chatbot_context'] = chatbot_context
            for res in response:
                if res['response_type'] == 'text':
                    chatHistory.append({'robot_is_sender': True, 'text': res['text']})
                    speak(res['text'])
            request.session['chatHistory'] = chatHistory
        # if the input is to change the sorting algo in the ideas list
        elif request.POST.get("sort")!=None:
            request.session['sort'] = request.POST.get("sort")
    # content is used for display in the template
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

    # note that we receive the text, complexity and expensiveness of ideas in one list from Watson Assistant
    # We have to process every 3 values into a dictionary
    if content.get('ideas')!=None:
        new_ideas = []
        i = 0
        while i < (len(content['ideas'])):
            new_ideas.append({'text': content['ideas'][i], 'complexity': content['ideas'][i+1], 'expensive': content['ideas'][i+2]})
            i+=3
        content['new_ideas'] = sortByKey(new_ideas, request.session['sort'])

    # We assign the id of each project by the user id of the chatbot because chatbot assign a unique id for each session
    content['id'] = request.session['chatbot_context']['global']['system']['user_id']

    # check what projects are in the user's account 
    # same as this part in dashboard
    if request.session.get(request.user.email)!=None:
        project = request.session.get(request.user.email)
    else:
        projectID = getProjectID(request.user.email)
        project = getProjectName(projectID)
        request.session[request.user.email] = project

    # if the context variable save is True, it means this session is finished and the data should be saved
    # it will call functions in dbconnection.py to run SQL commands
    # after that, reset the chat history and context in sessions
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
        'sort': request.session['sort'],
    }
    return render(request, 'designthinking/newdesign.html', context)

@login_required
def review(request, id):
    projectID = getProjectID(request.user.email)
    project = getProjectName(projectID)
    if 'sort' not in request.session:
        request.session['sort'] = 'default'
    
    # check that if this id is stored in this account 
    # if not, redirect the user back to the dashboard
    if id not in projectID:
        return redirect('dashboard')

    # check if the data on this project is saved in session 
    # if not ask DB2 database for it 
    if request.session.get(id):
        content = request.session.get(id)
    else:
        content = getProjectContent(id)
        request.session[id] = content
    
    # if the user makes a change to the record 
    if request.method == 'POST':
        # if the user want to delete an element
        if (request.POST.get('delete'))!=None:
            # table stores which table to delete from 
            # sequence stores which element to delete
            table = request.POST.get('name')
            sequence = request.POST.get('delete')
            rows = content[table]
            for row in rows:
                if row['sequence'] == sequence:
                    item = row
            deleteItem(table,item)

        # if the user want to delete an element
        textToAdd = request.POST.get('add')
        if textToAdd!=None and textToAdd!='':
            table = request.POST.get('name')
            # if the user is adding a new element to the empathy map
            # insert to two column table
            if "Empathy" in table:
                value = [id, textToAdd]
                insertSingleTwo(table, value)
            # if the user is adding a new element to the idea list
            # insert to four column table
            else:
                complexity = request.POST.get('complexity')
                expensive = request.POST.get('expensive')
                value = [id, complexity, expensive, textToAdd]
                insertSingleFour(table, value)
        # update the data stored in sessions
        content = getProjectContent(id)
        request.session[id] = content
    if request.POST.get("sort")!=None:
        request.session['sort'] = request.POST.get("sort")

    # always sort the idea list using the current sorting algo
    content['Ideas'] = sortByKey(content['Ideas'], request.session['sort'])
    context = {
        'content':content,
        'projects': project,
        'sort': request.session['sort'],
    }
    return render(request, 'designthinking/review.html', context)


@login_required
def helpPage(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid:
            form.save()
            messages.success(request, f'Message sent!')
            # message is sent to the current host email 
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



