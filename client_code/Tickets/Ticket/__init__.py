from ._anvil_designer import TicketTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ...Dashboard import Data
from ... import Validation


class Ticket(TicketTemplate):
  """This Form displays ticket and customer information for a single ticket. It also allows you to edit the ticket being displayed.
  
  Keyword Arguments:
    item: a row from the 'Tickets' Data Table
    
  A copy of this row from the 'Tickets' table is initialised as self.ticket_copy in form_refreshing_data_bindings()
  
  """
  
  def __init__(self, **properties):
    self.ticket_copy = {}
    # This returns a list of tuples to form the items of the category_dropdown. 
    # category_dropdown is data bound to self.categories
    self.categories = Data.CATEGORIES
    # This returns a list of tuples to form the items of the priority_dropdown. 
    # priority_dropdown is data bound to self.priorities
    self.priorities = Data.PRIORITIES
    # This returns a list of tuples to form the items of the status_dropdown. 
    # status_dropdown is data bound to self.status
    self.status = Data.STATUS
    users = anvil.server.call('get_users')
    # agent_dropdown is data bound to self.agents
    self.agents = [(x['email'], x) for x in users]
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
  def form_refreshing_data_bindings(self, **event_args):
    # If self.item exists and ticket_copy not yet initialised, initialise it. 
    if self.ticket_copy == {} and self.item:
      self.ticket_copy = dict(list(self.item))

  # Change the title of the ticket
  def ticket_title_edit(self, **event_args):
    if self.title_box.text is not "":
      self.update_ticket(**event_args)
    else:
      self.title_box.text = self.item['title']
      alert("Please give your ticket a title")
  
  # Change ticket details
  def update_ticket(self, sender, **event_args):
    tick_validation_errors = Validation.get_ticket_settings_errors(self.ticket_copy)
    if tick_validation_errors:
      alert("The following fields are missing for your customer: \n{}".format(
        ' \n'.join(word for word in cust_validation_errors)
      ))
    elif sender is self.date_picker_1 and self.date_picker_1.date is None:
      self.date_picker_1.date = self.item['due']
      alert("Please choose a due date")
    else:
      anvil.server.call('update_ticket', self.item, self.ticket_copy)
      self.ticket.refresh_data_bindings()
      self.ticket.set_overdue_closed_label()
      








