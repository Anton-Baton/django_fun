from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Category, Page
from .forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from bing_search import run_query


def set_visits_via_client_cookies(request, response):

    visits = int(request.COOKIES.get('visits', '1'))
    reset_last_visit_time = False
    if 'last_visit' in request.COOKIES:
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')

        # TODO: this is a little strange - not different days, but distance
        # of one day between visits
        if (datetime.now() - last_visit_time).days > 0:
            reset_last_visit_time = True
            visits += 1
    else:
        reset_last_visit_time = True
        # TODO: do I really need it?
        # context['visits'] = visits
        # response = render(request, 'rango/index.html', context)

    if reset_last_visit_time:
        response.set_cookie('last_visit', datetime.now())
        response.set_cookie('visits', visits)


def set_visits_via_server_session(request):

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')

        if (datetime.now() - last_visit_time).days > 0:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits


def index(request):
    # return HttpResponse('allah<br/><a href="/rango/about"/>About</a>')
    # context = {'boldmessage': 'Bold'}
    # return render(request, 'rango/index.html', context)

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context = {'categories': category_list, 'pages': pages_list}

    # Call here, cause need to update request
    set_visits_via_server_session(request)

    response = render(request, 'rango/index.html', context)

    # Call here, cause need to update response
    # set_visits_via_client_cookies(request, response)

    return response


def category(request, category_name_slug):
    context = {'category_name': category_name_slug, 'query': category_name_slug}
    if request.method == 'POST':
        result_list = []
        if request.method == 'POST':
            query = request.POST['query'].strip()
            context['query'] = query
            if query:
                result_list = run_query(query)
        context['result_list'] = result_list

    try:
        cat = Category.objects.get(slug=category_name_slug)
        cat.views += 1
        cat.save()
        context['category'] = cat

        # context['category_name'] = cat.name

        pages = Page.objects.filter(category=cat).order_by('-views')
        context['pages'] = pages
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', context)


def about(request):
    # return HttpResponse('test project<br/><a href="/rango/">Index</a>')
    visits = request.session['visits']
    if visits:
        visit_msg = 'You visited site for {} times'.format(visits)
    else:
        visit_msg = 'You are here for the first time'
    return render(request, 'rango/about.html', {'visit_msg': visit_msg})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            # TODO: check if this is a good way!
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    # context = {}
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
                # time = datetime.now()
                # page.first_visit = time
                # page.last_visit = time
                page.save()

                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context)


"""
def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                msg = 'Your Rango account is disabled!'
                return render(request, 'rango/login_trouble.html', {'trouble_message': msg})
        else:
            print 'Invalid login credentials: {0}, {1}'.format(username, password)
            msg = 'Invalid credentials.'
            return render(request, 'rango/login_trouble.html', {'trouble_message': msg})

    else:
        return render(request, 'rango/login.html', {})
"""


@login_required
def restricted(request):
    # return HttpResponse('Only for homies.')
    pm = 'Hi, nigga!'
    return render(request, 'rango/restricted.html', {'private_message': pm})

"""
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
"""


@login_required
def user_profile(request):
    # user = request.user
    return render(request, 'rango/user_profile.html', {})


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    if request.method == 'GET':
        # page_id = request.GET.get('page_id', None)
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page = Page.objects.get(pk=page_id)
            page.views += 1
            page.last_visit = datetime.now()
            # print '>>>>> Last time >>>> ', page.last_visit
            page.save()
            return redirect(page.url)
    return HttpResponseRedirect('/rango/')

