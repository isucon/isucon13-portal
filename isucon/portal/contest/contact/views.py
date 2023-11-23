from django.shortcuts import get_object_or_404, redirect, render
from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.contest.contact.forms import NewTicketForm, TicketCommentForm
from isucon.portal.contest.contact.models import Ticket
from isucon.portal.contest.decorators import team_is_now_on_contest
from django.contrib import messages


@team_is_authenticated
@team_is_now_on_contest
def ticket_list(request):
    tickets = Ticket.objects.filter(owner__team=request.user.team).order_by("-created_at")

    context = {
        "tickets": tickets,
    }
    return render(request, "ticket_list.html", context)

@team_is_authenticated
@team_is_now_on_contest
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.filter(owner__team=request.user.team), pk=pk)
    comments = ticket.ticketcomment_set.all()

    if request.method == "POST":
        form = TicketCommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.owner = request.user
            comment.save()
            ticket.updated_at = comment.created_at
            ticket.save()
    
    form = TicketCommentForm()

    context = {
        "ticket": ticket,
        "comments": comments,
        "form": form,
    }
    return render(request, "ticket_detail.html", context)

@team_is_authenticated
@team_is_now_on_contest
def ticket_new(request):
    form = NewTicketForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.ticket = ticket
            ticket.owner = request.user
            ticket.save()
            messages.success(request, "チケットを作成しました")
            return redirect("ticket_detail", pk=ticket.pk)
        else:
            messages.error(request, "チケットの作成に失敗しました")

    context = {
        "form": form,
    }
    return render(request, "ticket_new.html", context)
