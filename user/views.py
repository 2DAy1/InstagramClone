from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from .forms import ProfileForm
from .models import Profile


User = get_user_model()


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'user/profile.html',
                  {'profile': profile, 'profile_user':profile.user})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm
from .models import Profile


@login_required
def edit_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Зберігаємо ненавантжувальні поля
            profile = form.save(commit=False)

            # Беремо файл з чистих даних
            avatar_file = form.cleaned_data.get('avatar')
            if avatar_file:
                # Видаляємо поточне значення з __dict__, щоб спрацював дескриптор
                if 'avatar' in profile.__dict__:
                    del profile.__dict__['avatar']
                # Тепер profile.avatar — це FieldFile, і в нього є .save()
                profile.avatar.save(avatar_file.name, avatar_file)

            # Фінальний save
            profile.save()
            return redirect('user:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'user/edit_profile.html', {'form': form})


