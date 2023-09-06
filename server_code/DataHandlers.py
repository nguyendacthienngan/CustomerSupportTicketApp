import anvil.secrets
import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta, date
from . import Data
from . import Validation
import anvil.pdf

authenticated_callable = anvil.server.callable(require_user=True)
CLOSED = Data.CLOSED
OPEN = Data.OPEN
URGENT = Data.URGENT
OUTGOING = Data.OUTGOING

# Ticket functions 
@authenticated_callable
def get_tickets(sort, filters={}, date_filter={}):
  if filters.get('owner') and filters['owner'] == Data.NO_AGENTS_SELECTED:
    filters['owner'] = None
  ascending = sort != 'date'
  closed_status = CLOSED
  # Condition on date filters here then pass to filters if acceptable
  start = date_filter.get('start') or datetime(1900, 1, 1, 0, 0, 0)
  end = date_filter.get('end') or datetime.now()
  end += timedelta(days=1)
  filters['date'] = q.between(start, end)
  if filters.get('status') == CLOSED:
    closed_start = date_filter.get('closed_start') or datetime(1900, 1, 1)
    closed_end = date_filter.get('closed_end') or datetime.now()
    closed_end += timedelta(days=1)
    filters['closed'] = q.between(closed_start, closed_end)
  return app_tables.tickets.search(tables.order_by(sort, ascending=ascending), **filters)

@authenticated_callable
def get_customer_tickets(filters={}):
  tickets = app_tables.tickets.search(tables.order_by('date', ascending=False), **filters)
  tick_and_messages = []
  for t in tickets:
    messages = app_tables.messages.search(tables.order_by("date", ascending=False), ticket=t)
    first_message = messages[len(messages) - 1]
    data = {'ticket':t, 'message':first_message}
    tick_and_messages.append(data)
  return tick_and_messages
    

@authenticated_callable
@tables.in_transaction
def add_ticket(ticket_dict, text, customer):
  # If this customer already exists in the database, don't re-check for errors
  if app_tables.customers.has_row(customer):
    cust_validation_errors = None
  else:
    cust_validation_errors = Validation.get_customer_errors(customer)
  tick_validation_errors = Validation.get_ticket_errors(ticket_dict)
  if tick_validation_errors or cust_validation_errors:
    raise Exception('Something went wrong')
  else:
    if not app_tables.customers.has_row(customer):
      customer = add_customer(customer)
    current_ticket_row = app_tables.currentticketno.get()
    ticket = app_tables.tickets.add_row(
        customer=customer, 
        status=app_tables.status.get(name="Open"), 
        date=datetime.now(),
        number=current_ticket_row['number'],
        **ticket_dict
      )
    # Increment current ticket number
    current_ticket_row['number'] += 1
    app_tables.messages.add_row(
        date=datetime.now(),
        ticket=ticket,
        type=app_tables.types.get(name="INTERNAL_NOTE"),
        details=text,
        agent=anvil.users.get_user()
    )
    return ticket
  

@anvil.email.handle_message()
def message_handler(msg):
  msg.reply(text="Thank you for your message. We aim to get back to you in 3 working days.")
  
  cust_row = app_tables.customers.get(email=msg.envelope.from_address)
  if not cust_row:
    names = msg.addressees.from_address.name.split(" ", 1)
    cust_row = app_tables.customers.add_row(
      email=msg.envelope.from_address,
      first_name=names[0],
      last_name=names[1],
      company="",
      title="",
      created=datetime.now()
    )
  current_ticket_row = app_tables.currentticketno.get()
  ticket_row = app_tables.tickets.add_row(
                title=msg.subject,
                category=Data.NEW_CATEGORY,
                priority=Data.NEW_PRIORITY,
                status=Data.OPEN,
                date=datetime.now(),
                customer=cust_row,
                due=date.today() + timedelta(days=3),
                owner=app_tables.users.get(email="demo@anvil.works"),
                number=current_ticket_row['number']
                )
  current_ticket_row['number'] += 1
  msg_row = app_tables.messages.add_row(
              details=msg.text,
              date=datetime.now(),
              ticket=ticket_row,
              type=Data.INCOMING
  )

  
@authenticated_callable
def add_message(message_dict, ticket):
  message_validation_errors = Validation.get_message_errors(message_dict)
  if message_validation_errors:
    raise Exception("Something went wrong")
  else:
    app_tables.messages.add_row(
        date=datetime.now(),
        ticket=ticket,
        agent=anvil.users.get_user(),
        **message_dict
    )
  if message_dict['type'] == Data.OUTGOING:
    anvil.email.send(
      to=ticket['customer']['email'],
      from_name="Anvil Support",
      subject=f"Re: {ticket['title']}",
      text=message_dict['details']
    )
  
@authenticated_callable
def update_ticket(ticket, ticket_dict):
  tick_validation_errors = Validation.get_ticket_settings_errors(ticket_dict)
  if tick_validation_errors:
    raise Exception("Something went wrong")
  else:
    if app_tables.tickets.has_row(ticket):
      # If ticket is newly closed
      if ticket_dict['status'] == CLOSED and not ticket['status'] == CLOSED:
        ticket_dict['closed'] = datetime.now()
      ticket.update(**ticket_dict)  
    
@authenticated_callable
def update_ticket_priority(ticket, priority):
  if app_tables.tickets.has_row(ticket):
    ticket.update(priority=priority)  
    
@authenticated_callable
@tables.in_transaction
def close_tickets(tickets):
  for t in tickets:
    messages = app_tables.messages.search(ticket=t)
    for m in messages:
      if app_tables.messages.has_row(m):
        m.delete()
    if app_tables.tickets.has_row(t):
      t.delete()
  
@authenticated_callable
def add_customer(cust_dict):
  cust_dict['created'] = datetime.now()
  return app_tables.customers.add_row(**cust_dict)

@authenticated_callable
def update_customer(customer, customer_dict):
  if app_tables.customers.has_row(customer):
    cust_validation_errors = Validation.get_customer_errors(customer_dict)
    if cust_validation_errors:
      raise Exception('Something went wrong')
    else:
      customer.update(**customer_dict)  
    
@authenticated_callable
@tables.in_transaction
def delete_customers(customers):
  for c in customers:
    tickets = app_tables.tickets.search(customer=c)
    for t in tickets:
      messages = app_tables.messages.search(ticket=t)
      for m in messages:
        if app_tables.messages.has_row(m):
          m.delete()
      if app_tables.tickets.has_row(t):
        t.delete()
    if app_tables.customers.has_row(c):
      c.delete()
      
@authenticated_callable
def get_messages(ticket):
  return app_tables.messages.search(tables.order_by("date", ascending=False), ticket=ticket)

@authenticated_callable
def get_dashboard_data(date_filters={}, dash_filters={}):
  resolved_tickets, new_tickets = get_ticket_data(date_filters, dash_filters)
  headline_stats = get_headline_dash_stats(date_filters, dash_filters)
  progress_dash_stats = get_progess_data(resolved_tickets, new_tickets, date_filters, dash_filters)
  resolution_data = get_resolution_data(resolved_tickets, new_tickets, date_filters, dash_filters)
  return headline_stats, progress_dash_stats, resolution_data

def get_ticket_data(date_filters, dash_filters):
  resolved_tickets = app_tables.tickets.search(
    closed=q.between(date_filters['start'], date_filters['end'], max_inclusive=True),
    status=CLOSED,
    **dash_filters
  )
  new_tickets = app_tables.tickets.search(
    date=q.between(date_filters['start'], date_filters['end'], max_inclusive=True), 
    **dash_filters
  )
  return resolved_tickets, new_tickets

def get_headline_dash_stats(date_filters, dash_filters):
  tickets = app_tables.tickets.search(date=q.between(date_filters['start'], date_filters['end']), **dash_filters)
  unassigned = len([x for x in tickets if x['owner'] == None])
  unresolved = len([x for x in tickets if x['closed'] == None])
  # priority as constant
  if dash_filters.get('category'):
    # Category is urgent for this search so only allow through category from dash_filters
    urgent = len([x for x in tickets if x['priority'] == URGENT and x['category'] == dash_filters['category']])
  else:
    urgent = len([x for x in tickets if x['priority'] == URGENT])
  prev_start = date_filters['start'] - timedelta(days=date_filters['time_period'])
  prev_tickets = app_tables.tickets.search(owner=None, date=q.between(prev_start, date_filters['start']), **dash_filters)
  d_unassigned = len([x for x in prev_tickets if x['owner'] == None]) - unassigned
  d_unresolved = len([x for x in prev_tickets if x['closed'] == None]) - unresolved
  if dash_filters.get('category'):
    # Category is urgent for this search so only allow through category from dash_filters
    d_urgent = len([x for x in prev_tickets if x['priority'] == URGENT and x['category'] == dash_filters['category']]) - urgent
  else:
    d_urgent = len([x for x in prev_tickets if x['priority'] == URGENT]) - urgent
  return {
    'unassigned': {'delta':-d_unassigned, 'number':unassigned},
    'unresolved':{'delta':-d_unresolved, 'number':unresolved},
    'urgent':{'delta':-d_urgent, 'number':urgent}
  }

@authenticated_callable
def get_progess_data(resolved_tickets, new_tickets, date_filters, dash_filters):
  # Get the type of an outoing email from Support
  # Tickets closed on first reply are those that are both closed AND have only one reply to the customer from internal
  closed_on_first = [t for t in resolved_tickets if len(app_tables.messages.search(ticket=t, type=OUTGOING)) == 1]
  # This returns ALL new customers over the period. Need to then apply dashboard filters to only return new_customers with tickets that match the filters
  all_new_customers = app_tables.customers.search(
    created=q.between(date_filters['start'], date_filters['end'], max_inclusive=True),
  )
  new_customers_resolved = [x['customer'] for x in resolved_tickets if x['customer'] in all_new_customers]
  new_customers_unresolved = [x['customer'] for x in new_tickets if x['customer'] in all_new_customers]
  new_customers = list(set().union(new_customers_resolved,new_customers_unresolved))
  # Returning customers are those with new tickets who aren't in new_customers
  returning_customers = set([x['customer'] for x in new_tickets if x['customer'] not in new_customers])
  # Returning customers also includes those whose tickets have been resolved during the period (and aren't already accounted for)
  returning_customers.union(set([x['customer'] for x in resolved_tickets if x['customer'] not in new_customers]))
  return {
    'resolved': {
      'total_resolved': len(resolved_tickets), 'closed_on_first':len(closed_on_first)
     }, 
    'customers':{
      'new_customers':len(new_customers), 'returning_customers':len(returning_customers)
     }
  }


@authenticated_callable
def get_resolution_data(resolved_tickets, new_tickets, date_filters, dash_filters):
  dates = []
  res = []
  unres = []
  for day in (date_filters['start'] + timedelta(days=n) for n in range(date_filters['time_period'])):
    dates.append(day.strftime('%A, %d'))
    r = len([x for x in resolved_tickets if x['closed'].date() == day])
    res.append(r)
    u = len([x for x in new_tickets if not x['closed'] and x['date'].date() == day])
    unres.append(u)
  data = {'resolved':res, 'unresolved':unres}
  return {'dates':dates, 'data':data}

  
@authenticated_callable
def get_customers(filters={}):
  return app_tables.customers.search(tables.order_by('last_name', ascending=True), **filters)

# Maybe return a subset of this?
@authenticated_callable
def get_users():
  return app_tables.users.search()

@authenticated_callable
def login_demo_user():
  demo_user = app_tables.users.get(email="demo@anvil.works")
  user = anvil.users.force_login(demo_user)
  return user




