from django.http import HttpResponse
from django.shortcuts import render, redirect
from rango.models import Category, Page, UserProfile, User
from datetime import datetime
from django.template.defaultfilters import slugify

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rango.bing_search import run_query

@login_required
def auto_add_page(request):
    context_dict = {}
    cat_id = None
    url = None
    title = None

    if request.method == 'GET':
        title = request.GET['title']
        url = request.GET['url']
        cat_id = request.GET['category_id']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if cat_list.count() > max_results:
            cat_list = cat_list[:max_results]

    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})

@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

def public_profile(request, username_slug):
    found = True
    try:
        profile = UserProfile.objects.get(slug=username_slug)
    except UserProfile.DoesNotExist:
        found = False

    return render(request, 'rango/public_profile.html', {'found': found, 'profile': profile})

def profile_directory(request):
    profiles = UserProfile.objects.all()
    try:
        active_profile = UserProfile.objects.get(user=request.user)
    except:
        user_slug = None

    return render(request, 'rango/profile_directory.html', {'active_profile': active_profile, 'profiles': profiles})

def profile(request):
    registered = False
    user_profile = None
    if request.user.is_authenticated():
        if UserProfile.objects.filter(user=request.user).exists():
            user_profile = UserProfile.objects.get(user=request.user)
            registered = True
    return render(request, 'rango/profile.html', {'profile': user_profile, 'registered': registered})

def register_profile(request):
    if request.user.is_authenticated():
        user = request.user
        registered = False
    
        if request.method == 'POST':
            profile_form = UserProfileForm(request.POST)

            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = user

                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
                    profile.save()
                    registered = True
            else:
                print profile_form.errors

        else:
            profile_form = UserProfileForm()
    
    return render(request,
        'registration/profile_registration.html',
        {'profile_form': profile_form, 'registered': registered})

def track_url(request):
    url = 'index'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            try:
                page_id = request.GET['page_id']
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass
                
    return redirect(url)

def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def index(request):
    # query the database for a list of all categories currently stored
    # order the categories by number of likes in descending order
    # retrieve the top 5 only - or all if less than 5
    # place the list in our context_dict dictionary which will be passed to the template engine
    category_list = Category.objects.all()
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
            # update the last visit cookie
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response

def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    if request.method == "POST":
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages

        # We also add the category object from the database to the context dictionary.
        # We'll ues this in the template to verify that the category exists.
        context_dict['category'] = category

        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html', { 'visits': count})

@login_required
def add_category(request):
    # A HTTP POST?
        if request.method == 'POST':
            form = CategoryForm(request.POST)

            # Have we been provided with a valid form?
            if form.is_valid():
                # Save the new category to the database.
                form.save(commit=True)

                # Now call the index() view.
                # The user will be shown the homepage.
                return index(request)
            else:
                # The supplied form contained errors - just print them to the terminal.
                print form.errors
        else:
            # If the request was not a POST, display the form to enter details.
            form = CategoryForm()

            # Bad form (or form details), no form supplied...
            # Render the form with error message (if any).
        return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)
