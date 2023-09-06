from ._anvil_designer import TicketsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ...Dashboard import Data
from datetime import date


class Tickets(TicketsTemplate):
  """This Form is responsible for passing user-defined filters to the 'TicketList' Form.
  
  The filtering logic is collected from user inputs and sent to the 'TicketList' Form to be processed. 
  """
  
  def __init__(self, initial_filters=None, initial_date_filters=None, **properties):
    """Collect filters, and send them to the TicketList Form to retrieve a list of tickets.
    
    Arguments: 
      initial_filters (optional): dict of filters on the ticket view
      initial_date_filters (optional): dict of date filters on the ticket view
    """
    
    self.filters = initial_filters or {'status': Data.OPEN}
    self.date_filter = initial_date_filters or {}
    # This returns a list of tuples to form the items of the category_dropdown. 
    # category_dropdown is data bound to self.categories
    self.categories = Data.CATEGORIES
    # This returns a list of tuples to form the items of the priority_dropdown. 
    # priority_dropdown is data bound to self.priorities
    self.priorities = Data.PRIORITIES
    # This returns a list of tuples to form the items of the status_dropdown. 
    # status_dropdown is data bound to self.status
    self.status = Data.STATUS
    # customer_dorpdown is data bound to self.customers
    self.customers = [(f"{x['first_name']} {x['last_name']}", x) for x in anvil.server.call('get_customers')]
    # agent_dropdown is data bound to self.owners
    self.owners = [(x['email'], x) for x in anvil.server.call('get_users')]
    # There are two options for the 'agents' Dropdown:
    # 1) Show tickets belonging to any agent - do this by selecting the placeholder which has the value None
    # 2) Show tickets that have not been assigned to an agent - do this by selecting Data.NO_AGENTS_SELECTED
    # We need to manually add option (2) to the agents dropdown
    self.owners.append(('None', Data.NO_AGENTS_SELECTED))
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Call load_tickets on the 'TicketList' Form, and pass through any filters
    self.ticket_list.load_tickets(filters=self.filters, date_filter=self.date_filter)
    # Any code you write here will run when the form opens.
    
  def load_tickets(self, sender, **event_args):
    # If the filters are changed, de-select any currently selected tickets. This is done on the 'TicketList' Form
    self.ticket_list.clear_selected_link_click()
    # If a filter has been removed (value set to None), remove the key from self.filters
    if sender.selected_value is None:
      self.filters = {k: v for k, v in self.filters.items() if v is not None}
    # Send filters to the TicketList Form to load tickets from the server
    self.ticket_list.load_tickets(filters=self.filters, date_filter=self.date_filter)
    
  def clear_filters_link_click(self, **event_args):
    self.filters = {}
    self.date_filter = {}
    self.refresh_data_bindings()
    self.ticket_list.sort_dropdown.selected_value = 'Date'
    self.ticket_list.load_tickets(self.filters)
    
  def load_tickets_by_date(self, **event_args):
    # Called when any of the date filters change
    self.ticket_list.load_tickets(filters=self.filters, date_filter=self.date_filter)


