from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView, TemplateView  # noqa
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count, Avg
from booking.forms import CalendlyUriForm
from booking.models import Payment, TutoringSession
from calendly.views import introspect_access_token
from tutor_market.forms import RatingForm, TutorForm
from tutor_market.models import Tutor, Rating
from django.urls import reverse_lazy
from .models import Tutor, Student, Conversation
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Tutor, Message
from .forms import MessageForm



# def start_conversation(request):
#     """
#     Create or retrieve a conversation between a student and a tutor.
#     """
#     if request.method == "POST":
#         tutor_id = request.POST.get("tutor_id")
#         student_id = request.POST.get("student_id")

#         tutor = get_object_or_404(Tutor, id=tutor_id)
#         student = get_object_or_404(Student, id=student_id)

#         conversation, created = Conversation.objects.get_or_create(
#             tutor=tutor,
#             student=student
#         )

#         return JsonResponse({
#             "conversation_id": conversation.id,
#             "created": created  # True if a new conversation was created
#         })
        
from .models import Conversation, Message
from django.contrib.auth.decorators import login_required

@login_required
def send_message(request):
    """
    Send a message in a conversation.
    """
    if request.method == "POST":
        conversation_id = request.POST.get("conversation_id")
        content = request.POST.get("content")

        conversation = get_object_or_404(Conversation, id=conversation_id)
        sender = request.user

        if sender not in [conversation.tutor.user, conversation.student.user]:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )

        return JsonResponse({
            "message": "Message sent successfully",
            "message_id": message.id
        })


@login_required
def get_messages(request, conversation_id):
    """
    Retrieve messages in a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in [conversation.tutor.user, conversation.student.user]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    messages = conversation.messages.order_by('timestamp').values('sender__username', 'content', 'timestamp')

    return JsonResponse(list(messages), safe=False)





@login_required
def conversation_list(request):
    conversations = request.user.conversations.all()
    return render(request, 'conversation_list.html', {'conversations': conversations})


@login_required
def chat(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
        return redirect('chat', conversation_id=conversation.id)
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'chat.html', {'conversation': conversation, 'messages': messages})












@login_required
def start_conversation(request, tutorID):
    student = request.user
    tutor = get_object_or_404(Tutor, id=tutorID)
    messages = Message.objects.filter(
        (Q(sender=student) & Q(recipient=tutor.user)) | (Q(sender=tutor.user) & Q(recipient=student))
    ).order_by('timestamp')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = student
            new_message.recipient = tutor.user
            new_message.save()
            return redirect('start_conversation', tutorID=tutorID)
    else:
        form = MessageForm()

    context = {
        'tutor': tutor,
        'student': student,
        'messages': messages,
        'form': form,
    }
    return render(request, 'tutor_market/includes/chat.html', context)

from django.http import Http404
@login_required
def tutor_messages(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            recipient_email = request.POST.get('recipient_email')
            recipient = get_object_or_404(User, email=recipient_email)
            
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            
            messages.success(request, f'Message sent to {recipient.email}')
            return redirect('tutor_messages')
        else:
            messages.error(request, 'Failed to send message. Please try again.')
    else:
        form = MessageForm()

    return render(request, 'tutor_market/includes/tutor_messages.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'form': form,
    })
  

# def chat_view(request, tutor_id):
#     tutor = Tutor.objects.get(id=tutor_id)
#     messages = Message.objects.filter(sender__in=[request.user, tutor.user], recipient__in=[request.user, tutor.user]).order_by('timestamp')
#     form = MessageForm()

#     if request.method == "POST":
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.sender = request.user
#             message.recipient = tutor.user
#             message.save()
    
#     return render(request, 'chats.html', {'tutor': tutor, 'messages': messages, 'form': form, 'user': request.user})

def chats_view(request, tutorID):
    tutor = get_object_or_404(Tutor, id=tutorID)
    chats = Chat.objects.filter(participants=request.user).order_by('-last_message__timestamp')
    return render(request, 'chats.html', {'chats': chats, 'tutor': tutor})




def tutor_list_view(request):
    """
    Function-based view for listing all tutors in the system.

    This view handles the filtering and sorting of tutors based on various
    parameters provided in the request.GET query parameters.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML template with the list of tutors, filtered and sorted
    based on the request parameters.
    """
    tutor_list = Tutor.objects.filter(profile_status=True)
    subjects = None
    values = None
    query = None
    sorting = 'name'

    if request.GET:
        if 'subject' in request.GET:
            subjects = request.GET.getlist('subject')
            q_arguments = Q()
            for subject in subjects:
                q_arguments |= Q(subjects__name__icontains=subject)
            tutor_list = tutor_list.filter(q_arguments).distinct()

        if 'teachingvalue' in request.GET:
            # -> Credit for getting values from a list of query parameters: https://docs.djangoproject.com/en/5.0/ref/request-response/#querydict-objects # noqa
            values = request.GET.getlist('teachingvalue')
            q_arguments = Q()
            for value in values:
                # -> Credit for special add operator: https://stackoverflow.com/questions/29399653/python-operator-meaning  # noqa
                q_arguments |= Q(values__name__icontains=value)
            tutor_list = tutor_list.filter(q_arguments).distinct()

        if 'q' in request.GET:
            query = request.GET['q']

            queries = Q(
                display_name__icontains=query) | Q(
                description__icontains=query) | Q(
                catch_phrase__icontains=query) | Q(
                    subjects__name__icontains=query) | Q(
                        values__name__icontains=query)
            # -> Credit for returning distinct results: https://docs.djangoproject.com/en/5.0/ref/models/querysets/#distinct  # noqa
            tutor_list = tutor_list.filter(queries).distinct()

        if 'sorting' in request.GET:
            sorting = request.GET['sorting']
            if sorting == 'name':
                tutor_list = tutor_list.order_by('display_name')
            if sorting == 'cheapest':
                tutor_list = tutor_list.order_by('hourly_rate')
            if sorting == 'highest-rated':
                # -> Credit for default value in Avg: https://docs.djangoproject.com/en/5.1/ref/models/database-functions/#coalesce  # noqa
                tutor_list = tutor_list.annotate(avg_rating=Avg(
                    'ratings__score', default=0)).order_by('-avg_rating')
            if sorting == 'most-reviews':
                # -> Credit for distinct results in annotations: https://docs.djangoproject.com/en/5.0/topics/db/aggregation/#combining-multiple-aggregations  # noqa
                tutor_list = tutor_list.annotate(num_ratings=Count(
                    "ratings", distinct=True)).order_by("-num_ratings")
            if sorting == 'most-expensive':
                tutor_list = tutor_list.order_by('-hourly_rate')

    # Pagination
    paginator = Paginator(tutor_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_term': query,
        'subjects': subjects,
        'values': values,
        'query': query,
        'sorting': sorting,
        'tutor_list': tutor_list,
    }
    return render(request, 'tutor_market/tutor_list.html', context)


def tutor_detail_view(request, pk):
    """
    View for displaying the details (Profile) of a tutor.
    If a POST request is made, a new review is added to the tutor's profile.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tutor.

    Returns:
        HttpResponse: The HTTP response object containing the rendered
        template.

    Raises:
        None

    """
    tutor = get_object_or_404(Tutor, pk=pk)
    existing_rating = None
    upcoming_sessions = None

    # Check if the tutor's profile is activated
    if not tutor.profile_status:
        messages.warning(
            request, ('To activate your profile, please connect your Calendly '
                      'account via your Dashboard.')
        )
        return redirect(reverse('tutor_list'))

    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(
            tutor=tutor, user=request.user).first()
        upcoming_sessions = TutoringSession.objects.filter(
            tutor__user=tutor.user, student=request.user)

        response_data = introspect_access_token(tutor)
        if 'error' in response_data:
            messages.warning(
                request, f"{response_data['error']}: "
                f"{response_data['error_description']}")
            messages.warning(
                request, ('There seems to be an issue with this Tutor\'s '
                          'Calendly connection. Please contact us for more '
                          'information.')
            )
            # Only print a message if there is an error.

    # Handle POST request for adding a review
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(
                request, 'You must be logged in to leave a review.')
            return redirect('tutor_detail', pk=pk)

        if request.user == tutor.user:
            messages.warning(
                request, 'You cannot leave a review on your own profile.')
            return redirect('tutor_detail', pk=pk)

        review_form = RatingForm(request.POST)

        # how do I do proper form validation?
        # If I do it witha CBV the invalid form will reload the page and add
        # a specific error message on the invalid fields.
        if not review_form.is_valid():
            messages.warning(request, 'Form was not valid. Please try again.')
            return redirect('tutor_detail', pk=pk)

        # Update the existing review or add a new review
        if existing_rating:
            existing_rating.score = review_form.cleaned_data['score']
            existing_rating.comment = review_form.cleaned_data['comment']
            existing_rating.save()
            messages.success(request, 'Review updated successfully.')
            return redirect('tutor_detail', pk=pk)

        review = review_form.save(commit=False)
        review.tutor = tutor
        review.user = request.user
        review.save()
        messages.success(request, 'Review added successfully.')
        return redirect('tutor_detail', pk=pk)

    review_counts = {}

    # Prepare data for rendering the template
    form = RatingForm()
    calendly_form = CalendlyUriForm()
    calendly_event_url = tutor.calendly_event_url
    rating_exists = True if existing_rating else False
    reviews = tutor.ratings.all()

    total_reviews = reviews.count()
    review_counts = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}}
    for score in range(1, 6):
        count = reviews.filter(score=score).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0

        review_counts[score] = {'count': count, 'percentage': percentage}

    # -> Credit for reversing the order of a dictionary: https://www.geeksforgeeks.org/ordereddict-in-python/  # noqa
    review_counts = OrderedDict(reversed(list(review_counts.items())))

    context = {
        'tutor': tutor,
        'form': form,
        'calendly_form': calendly_form,
        'calendly_event_url': calendly_event_url,
        'reviews': reviews,
        'review_counts': review_counts,
        'existing_review': rating_exists,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'tutor_market/tutor_detail.html', context)


class TutorCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new tutor profile.

    Inherits from LoginRequiredMixin and CreateView.
    """

    model = Tutor
    form_class = TutorForm
    template_name = 'tutor_market/add_tutor.html'
    success_message = 'Tutor profile created successfully.'

    def form_valid(self, form):
        """
        Checks if the current user already has a Tutor instance and if so,
        redirects to the tutor's detail page.

        Sets the user field of the form instance to the current user.

        Args:
            form (Form): The form instance containing the submitted data.

        Returns:
            HttpResponseRedirect: Redirects to the tutor's detail page if the
            user already has a tutor profile.
            super().form_valid(form): Calls the parent class's form_valid
            method if the user does not have a tutor profile.
        """
        if Tutor.objects.filter(user=self.request.user).exists():
            messages.warning(self.request, 'You already have a tutor profile.')
            return redirect('tutor_detail', pk=self.request.user.tutor.pk)

        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Builds the URL to the newly created tutor's detail page.

        Returns:
            str: The URL to the tutor's detail page.
        """
        return reverse('dashboard', kwargs={'pk': self.object.user.pk})


class TutorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    A view for updating a tutor's information.

    Inherits from UserPassesTestMixin and UpdateView.
    """

    model = Tutor
    form_class = TutorForm
    template_name = 'tutor_market/edit_tutor.html'
    permission_required = 'tutor_market.change_tutor'
    success_message = 'Tutor profile updated successfully.'

    def test_func(self):
        """
        Checks if the current user is the owner of the tutor object.

        Returns:
            bool: True if the current user is the owner of the tutor object,
            False otherwise.
        """
        if self.request.user == self.get_object().user:
            return True
        else:
            messages.warning(
                self.request, ('You do not have permission to update this '
                               'profile.')
            )
            return False

    def get_success_url(self):
        """
        Builds the URL to the updated tutor's detail page.

        Returns:
            str: The URL to the updated tutor's detail page.
        """
        return reverse('dashboard', kwargs={'pk': self.object.user.pk})


class TutorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    A view for deleting a tutor.

    This view allows tutors to delete their profiles. When a tutor deletes
    their profile, they will be reverted to being a student.

    Attributes:
        model (Model): The model class for the tutor.
        template_name (str): The name of the template used for rendering the
            delete confirmation page.
        permission_required (str): The permission required to access this view.
        success_url (str): The URL to redirect to after successful deletion.
        success_message (str): The success message to display after successful
            deletion.

    Methods:
        test_func(): Checks if the current user is the owner of the tutor
            profile.

    """

    model = Tutor
    template_name = 'tutor_market/tutor_confirm_delete.html'
    permission_required = 'tutor_market.delete_tutor'
    success_url = reverse_lazy('tutor_list')
    success_message = 'Tutor profile deleted successfully.'

    def test_func(self):
        """
        Checks if the current user is the owner of the tutor profile.

        Returns:
            bool: True if the current user is the owner of the tutor profile,
                False otherwise.
        """
        if self.request.user == self.get_object().user:
            return True
        else:
            messages.warning(
                self.request, ('You do not have permission to delete this '
                               'profile.')
            )
            return False


def student_dashboard(request, user):

    booking_history = TutoringSession.objects.filter(student=user)
    # -> Credit for greater or equal to lookup (gte): https://docs.djangoproject.com/en/5.0/ref/models/querysets/#gte  # noqa
    upcoming_sessions = booking_history.filter(
        start_time__gte=timezone.now()).filter(session_status='scheduled')
    # add payment details (future feature)
    # add liked tutors (future feature)
    payment_history = Payment.objects.filter(user=user)
    amount_of_unpaid_sessions = booking_history.filter(
        payment_complete=False).count()
    context = {
        'upcoming_sessions': upcoming_sessions,
        'booking_history': booking_history,
        'payment_history': payment_history,
        'amount_of_unpaid_sessions': amount_of_unpaid_sessions,
    }
    return render(request, 'tutor_market/student_dashboard.html', context)



def tutor_dashboard(request, user):
    tutor = Tutor.objects.get(user=user)

    # check if the tutor profile should be enabled or disabled
    if (tutor.calendly_access_token and tutor.calendly_event_url):
        tutor.profile_status = True
        tutor.save()
    else:
        tutor.profile_status = False
        tutor.save()

    booking_history = TutoringSession.objects.filter(
        tutor=tutor).order_by('start_time')
    upcoming_sessions = booking_history.filter(
        start_time__gte=timezone.now(), session_status='scheduled')[:3]
    pending_sessions = booking_history.filter(session_status='pending')
    users = User.objects.filter(sessions__tutor=tutor)
    users_and_sessions = {}
    for user in users:
        sessions = booking_history.filter(student=user)
        users_and_sessions[user] = sessions

    context = {
        'booking_history': booking_history,
        'pending_sessions': pending_sessions,
        'upcoming_sessions': upcoming_sessions,
        'users_and_sessions': users_and_sessions,
        'tutor': tutor,
    }
    return render(request, 'tutor_market/tutor_dashboard.html', context)


@login_required
def dashboard_view(request, pk):
    """
    Calls the appropriate dashboard view based on the user's role.
    Recieves a render request from the function it called and renders
    the appropriate dashboard view.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the user.

    Returns:
        HttpResponse: The response object containing the appropriate dashboard
            view.

    Raises:
        Http404: If the user with the given primary key does not exist.

    """
    user = get_object_or_404(User, pk=pk)
    connected_tutor_profile = Tutor.objects.filter(user=user).first()

    if request.user != user:
        messages.warning(
            request, ('You do not have permission to view this dashboard. We '
                      'redirected you to your own dashboard.')
        )
        return redirect('dashboard', pk=request.user.pk)

    if connected_tutor_profile:
        return tutor_dashboard(request, user)
    else:
        return student_dashboard(request, user)


@require_POST
@login_required
def update_session_status(request, pk):
    """
    View for updating the status of a tutoring session.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tutoring session to be updated.

    Returns:
        HttpResponseRedirect: A redirect response to the dashboard page of the
            tutor.

    Raises:
        Http404: If the tutoring session with the given primary key does not
            exist.
    """
    session = get_object_or_404(TutoringSession, pk=pk)

    if session.tutor.user != request.user:
        messages.warning(
            request, 'You do not have permission to update this session.')
        return redirect('dashboard', pk=session.tutor.user.pk)

    session.session_status = request.POST['status']
    session.save()
    messages.success(request, 'Session status updated successfully.')
    return redirect('dashboard', pk=session.tutor.user.pk)


class CalendlyInformationView(LoginRequiredMixin, TemplateView):
    """
    A view that renders the Calendly information page.

    Attributes:
        template_name (str): The name of the template to be rendered.
    """
    template_name = 'tutor_market/calendly_information.html'
