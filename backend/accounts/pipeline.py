from django.contrib.auth import get_user_model

def debug_pipeline(strategy, details, response, *args, **kwargs):
    print("=== SOCIAL_AUTH DETAILS ===")
    print(details)
    print("=== SOCIAL_AUTH RESPONSE ===")
    print(response)

def require_email(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email') or strategy.session_get('saved_email')
    if not email:
        strategy.session_set('partial_pipeline_backend', backend.name)
        return strategy.redirect('/accounts/require_email/')
    details['email'] = email



def avoid_duplicate_email(strategy, details, backend, user=None, *args, **kwargs):
    User = get_user_model()
    email = details.get('email')
    if email:
        try:
            user = User.objects.get(email__iexact=email)
            return {'is_new': False, 'user': user}
        except User.DoesNotExist:
            pass
    return {}