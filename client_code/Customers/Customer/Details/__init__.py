from ._anvil_designer import DetailsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .. import Customer


class Details(DetailsTemplate):
  """This Form is responsible for displaying Customer Information and Recent Tickets for the customer.
  
  Keyword Arguments:
    item: accepts a row from the Customers Data Table
          initialises this in the 'form_refreshing_data_bindings' method.
  """
  
  def __init__(self, **properties):
    self.customer_tickets = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def form_show(self, **event_args):
    # Disable the close button if opened from the Tickets view
    homepage = get_open_form()
    if homepage.ticket_form_open:
      self.close_pane_link.visible = False
      
  def close_pane_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.close_overlay()

  def edit_customer_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.add_customer_edit_overlay(item=self.item)

  def new_ticket_button_click(self, **event_args):
    """Open the 'NewTicket' Form""" 
    homepage = get_open_form()
    homepage.open_new_ticket_form(initial_customer=self.item)
  
  def form_refreshing_data_bindings(self, **event_args):
    # Initialise customer_tickets when self.item is present
    if self.customer_tickets is None and self.item:
      self.customer_tickets = anvil.server.call('get_customer_tickets', filters={'customer': self.item})

  def name_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.open_customer(item=self.item)






  


