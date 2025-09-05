from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile

def edit_profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None

    editing = request.GET.get('edit', 'false') == 'true'
    success = request.GET.get('success', 'false') == 'true'

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            # Handle "same as delivery" logic
            if form.cleaned_data.get('same_as_delivery'):
                profile.billingAddress = form.cleaned_data.get('deliveryAddress')
            profile.save()
            return redirect('edit_profile')  # Use named URL, not hardcoded path
        else:
            print(form.errors)
    else:
        form = ProfileForm(instance=profile, user=user)

    if editing or not profile:
        return render(request, 'app_user/profile.html', {'form': form, 'editing': True})
    else:
        return render(request, 'app_user/profile.html', {
            'profile': profile,
            'editing': False,
            'success': success
        })
