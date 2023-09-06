from ._anvil_designer import TicketRowTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, date
from ..... import Data


class TicketRow(TicketRowTemplate):
  """This Form is the ItemTemplate of the 'TicketList' Form."""
  
  def __init__(self, **properties):
    self.priorities = Data.PRIORITIES
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run when the form opens.
    # If the ticket is closed, add a 'closed' label to display the date it was closed
    if self.item['status'] == Data.CLOSED:
      self.status_label.visible = True
      self.status_label.role = "closed-panel"
      self.status_label_text.text = "CLOSED"
      self.status_label.text = self.item['closed'].strftime("%d %b")
      self.status_label.visible = True
    # If the ticket is overdue, add an 'overdue' label 
    elif self.item['due'] < date.today():
      self.status_label.visible = True
      self.status_label.role = "overdue-panel"
    else:
      self.status_label.visible = False

  def ticket_title_link_click(self, **event_args):
    # Navigate to the 'Tickets' Form if the ticket title is clicked
    homepage = get_open_form()
    homepage.open_ticket(item=self.item)
    
  def check_box_1_change(self, **event_args):
    if self.check_box_1.checked:
      # Raise event on the parent repeating panel if the ticket is selected
      self.parent.raise_event('x-select-ticket', ticket=self.item)
      self.role = "tickets-repeating-panel-selected"
    else:
      # Raise event on the parent repeating panel if the ticket is de-selected
      self.parent.raise_event('x-deselect-ticket', ticket=self.item)
      self.role = "tickets-repeating-panel"

  def cust_name_link_click(self, **event_args):
    # Navigate to the 'Customers.Customer' Form is the name is clicked
    homepage = get_open_form()
    homepage.open_customer(self.item['customer'])

  def priority_dropdown_change(self, **event_args):
    ticket_copy = dict(list(self.item))
    ticket_copy['priority'] = self.priority_dropdown.selected_value
    # Change the ticket priority if the dropdown is changed
    self.parent.raise_event('x-update-ticket-priority', ticket=self.item, ticket_dict=ticket_copy)
    



