from django.shortcuts import get_object_or_404, redirect, render
from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.contest.contact.forms import NewTicketForm, TicketCommentForm
from isucon.portal.contest.contact.models import Ticket
from isucon.portal.contest.decorators import team_is_now_on_contest
from django.contrib import messages


@team_is_authenticated
@team_is_now_on_contest
def ticket_list(request):
    tickets = Ticket.only_team_query_set(request.user.team).order_by("-created_at")
    public_tickets = Ticket.public_query_set().order_by("-created_at")

    context = {
        "tickets": tickets,
        "public_tickets": public_tickets,
    }
    return render(request, "ticket_list.html", context)

@team_is_authenticated
@team_is_now_on_contest
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.visible_query_set(request.user.team), pk=pk)

    form = TicketCommentForm()
    can_post_comment = ticket.owner.team.id == request.user.team.id and ticket.status != "closed"

    if request.method == "POST" and can_post_comment:
        form = TicketCommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.owner = request.user
            comment.save()
            ticket.updated_at = comment.created_at
            if ticket.status == "waiting":
                ticket.status = "accepted"
            ticket.save()
            messages.success(request, "チケットにコメントを送信しました")
            return redirect("ticket_detail", pk=ticket.pk)

    comments = []
    show_description = True
    if ticket.visibility == "public" or ticket.owner.team.id == request.user.team.id:
        comments = ticket.ticketcomment_set.all().order_by("-created_at")
    else:
        show_description = False
    
    ticket.ticketcomment_set.all().order_by("-created_at")
    context = {
        "ticket": ticket,
        "comments": comments,
        "show_description": show_description,
        "can_post_comment": can_post_comment,
        "form": form,
    }
    return render(request, "ticket_detail.html", context)

@team_is_authenticated
@team_is_now_on_contest
def ticket_close(request, pk):
    ticket = get_object_or_404(Ticket.only_team_query_set(request.user.team), pk=pk)
    ticket.status = "closed"
    ticket.save()
    messages.success(request, "チケットを解決済みにしました")
    return redirect("ticket_detail", pk=ticket.pk)


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
