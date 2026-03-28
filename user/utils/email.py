from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from pages.context_processors import page_settings



def send_html_email(subject, template, to_email, context=None, request=None):
    context = context or {}
    context.update(page_settings(request))

    if request:
        context["protocol"] = "https" if request.is_secure() else "http"
        context["domain"] = request.get_host()

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()