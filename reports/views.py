from django.shortcuts import render, get_object_or_404
from profiles.models import Profile
from django.http import JsonResponse
from .utils import get_report_image
from .models import Report
from django.views.generic import ListView, DetailView, TemplateView
from .forms import ReportForm
from django.core.files.storage import FileSystemStorage

import datetime
from django.utils import timezone

# Using xhtml2pdf in Django
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

import csv
from django.utils.dateparse import parse_date


# Authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = "reports/main.html"

    def get_queryset(self):
        profile = self.request.user.profile
        queryset = super().get_queryset()
        return queryset.filter(author=profile)


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = "reports/detail.html"


class UploadTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "reports/from_file.html"


@login_required
def create_report_view(request):
    if request.accepts("application/json"):
        name = request.POST.get("name")
        remarks = request.POST.get("remarks")
        image = request.POST.get("image")
        img = get_report_image(image)

        author = Profile.objects.get(user=request.user)
        Report.objects.create(name=name, remarks=remarks, image=img, author=author)
        return JsonResponse({"msg": "send"})
    return JsonResponse()


# Using xhtml2pdf in Django
@login_required
def render_pdf_view(request, pk):
    template_path = "reports/pdf.html"
    obj = get_object_or_404(Report, pk=pk)
    context = {"obj": obj}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")

    # if doqnload
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # if display
    response["Content-Disposition"] = 'filename="report.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response
