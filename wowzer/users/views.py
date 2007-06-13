#
# File: $Id$
#
"""This module is all of the views for the 'users' and 'groups'.
"""

# Django imports
#
from django import newforms as forms
from django.newforms import widgets
from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

# Django contrib.auth imports
#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

# Wowzer utility functions
#
from wowzer.utils import msg_user, TZ_CHOICES
from wowzer.main.decorators import breadcrumb

# Data models.
#
from django.contrib.auth.models import User, Group
from wowzer.main.models import UserProfile, Breadcrumb

############################################################################
#
class ActivateForm(forms.Form):
    active = forms.BooleanField()
    reason = forms.CharField(max_length = 128)

############################################################################
#
class EmailForm(forms.Form):
    email = forms.EmailField()

############################################################################
#
class UserField(forms.CharField):
    def clean(self, value):
        super(UserField, self).clean(value)
        try:
            User.objects.get(username=value)
            raise forms.ValidationError("Someone is already using this "
                                        "username. Please pick an other.")
        except User.DoesNotExist:
            return value

class SignupForm(forms.Form):
    username = UserField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label="Repeat your password")
    email = forms.EmailField()
    email2 = forms.EmailField(label="Repeat your email")

    def clean_email(self):
        if self.data['email'] != self.data['email2']:
            raise forms.ValidationError('Emails are not the same')
        return self.data['email']

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self,*args, **kwargs):
        self.clean_email()
        self.clean_password()
        return super(SignupForm, self).clean(*args, **kwargs)

class CreateUserForm(SignupForm):
    """The 'SignupForm' is meant to be used on a page where a user is
    submitting their own signup information. Such users can not set
    the staff bit. However, on the create user form, that only staff
    can access they can set who and who is not staff (yeah, this is a
    bit weak policy wise but it is all we need right now.)"""
    staff = forms.BooleanField()

    # IF 'notify' is true we will send the user email indicating that
    # their account has been created.
    #
    # XXX Warning, this email will contain their password!
    #
    send_email = forms.BooleanField()

############################################################################
#
def sendout_email(user, password):
    """This helper function will send out email to the given user
    indicating that their account has been created. It will include
    the password that was set on their account. """

    from django.core.mail import send_mail
    current_domain = Site.objects.get_current().domain
    subject = "Accounted created for %s" % current_domain
    message_template = loader.get_template('users/creation_email.txt')
    message_context = Context(\
        { 'site_url': 'http://%s/' % current_domain,
          'password_change_url' : 'http://%s/accounts/change_pw/' % current_domain,
          'username': user.username,
          'password': password })
    message = message_template.render(message_context)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    return

############################################################################
#
@login_required
@breadcrumb(name="User List")
def index(request):
    """The top level view of 'users'. This is a list view of all of the user
    objects.
    """

    # Staff users can see deactivated users. Everyone else can only
    # see active user accounts.
    #
    if request.user.is_staff:
        qs = User.objects.order_by('username')
    else:
        qs = User.objects.filter(active = True).order_by('username')

    return object_list(request, qs, paginate_by = 20,
                       template_name = "users/index.html")

############################################################################
#
@user_passes_test(lambda u: u.is_staff or u.has_perm("auth.create_user"))
def user_create(request):
    """Create a user. Very simplistic.
    """
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            u = User.objects.create_user(form.clean_data['username'],
                                         form.clean_data['email'],
                                         form.clean_data['password'])
            if form.clean_data['staff']:
                u.is_staff = True

            # Create an empty profile for this user.
            #
            profile = UserProfile(user = u)
            profile.save()

            # Every user is part of the group "system:everyone" and
            # "system:authenticated"
            #
            try:
                u.groups.add(Group.objects.get(name="system:everyone"),
                             Group.objects.get(name="system:authenticated"))
            except Group.DoesNotExist:
                pass

            # If the submitted asked us to notify the user via email
            # that their account was created, do so.
            #
            if form.clean_data['send_email']:
                sendout_email(u, form.clean_data['password'])

            msg_user(request.user, "User '%s' created." % u.username)
            HttpResponseRedirect(u.get_absolute_url())
    else:
        form = CreateUserForm()
    t = get_template("users/user_create.html")
    c = Context(request, { 'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def user_detail(request, username):
    """Simple display of a user object.
    """
    u = get_object_or_404(User, username = username)

    Breadcrumb.rename_last(request, "User %s's profile" % username)

    # The user detail page also shows their profile information. To make
    # things a little easier if they do not have a profile then we create
    # one for them.
    #
    # NOTE: Other parts of the system still must assume that a profile
    # may not exist for a user. We are doing this here to make the
    # form and form processing for user profiles a little simpler.
    #
    try:
        profile = u.get_profile()
    except ObjectDoesNotExist:
        profile = UserProfile(user = u)
        profile.save()
    ProfileForm = forms.models.form_for_instance(profile)
    ProfileForm.base_fields['timezone'].widget = \
                          widgets.Select(choices=TZ_CHOICES)
    ProfileForm.base_fields['markup'].widget = \
                          widgets.Select(choices=UserProfile.MARKUP_CHOICES)

    if request.method == "POST":
        # Only staff, or the user themselves, or someone with update
        # permission on the user can submit changes.
        #
        if not (request.user.is_staff or
                request.user.username == username or
                request.user.has_perm("auth.change_user", object = u)):
            return HttpResponseForbidden("You do not have the requisite "
                                         "permissions to edit this user.")

        # Now the user detail page had on it several different forms each with
        # their own submit button. We need to see which button was pushed
        # and process that form. For every form that was not processed
        # we need to create the empty with defaults.
        #

        # Their "profile" data.
        #
        if request.POST["submit"] == "Save profile":
            profile_form = ProfileForm(request.POST)
            if profile_form.is_valid():
                entry = profile_form.save(commit = False)

                # We need to post-convert any submitted 'signature' into
                # html we can use via their chosen markup language.
                #
                func, ignore = getattr(__import__("wowzer."+entry.markup,
                                                  '', '', ['']),
                                       "to_html"), {}
                entry.signature_html = func(entry.signature)
                entry.save()
                msg_user(request.user, "User '%s' profile updated." % \
                         u.username)
                return HttpResponseRedirect(u.get_absolute_url())
        else:
            profile_form = ProfileForm()

        # Their "email" data.. ie: what they can edit in the user model.
        #
        if request.POST["submit"] == "Change email address":
            email_form = EmailForm(request.POST)
            if email_form.is_valid():
                u.email = email_form.clean_data['email']
                u.save()
                msg_user(request.user, "User '%s' email address updated." % \
                         u.username)
                return HttpResponseRedirect(u.get_absolute_url())
        else:
            email_form = EmailForm()

        # Finally the "activate" "deactivate" form. We only accept this
        # one if the user is staff.
        #
        if request.POST["submit"][-7:] == "ctivate" and request.user.is_staff:
            activate_form = ActivateForm(request.POST)
            if activate_form.is_valid():
                if activate_form.clean_data['active']:
                    u.is_active = True
                    msg_user(request.user, "User '%s' activated." % \
                             u.username)
                else:
                    u.is_active = False
                    msg_user(request.user, "User '%s' deactivated." % \
                             u.username)
                return HttpResponseRedirect(u.get_absolute_url())
        else:
            activate_form = ActivateForm()
    else:
        # This was a GET not a POST, so just create forms with default values.
        #
        profile_form = ProfileForm()
        email_form = EmailForm({'email' : u.email })
        activate_form = ActivateForm({'active' : u.is_active })

    t = get_template("users/user_detail.html")
    c = Context(request, {'object'        : u,
                          'profile'       : profile,
                          'email_form'    : email_form,
                          'profile_form'  : profile_form,
                          'activate_form' : activate_form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
def group_list(request):
    raise NotImplemented

############################################################################
#
@login_required
def group_detail(request):
    raise NotImplemented

############################################################################
#
@login_required
def group_index(request):
    raise NotImplemented

############################################################################
#
@login_required
def group_create(request):
    raise NotImplemented

############################################################################
#
@login_required
def group_delete(request):
    raise NotImplemented

