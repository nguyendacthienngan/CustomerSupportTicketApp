from ._anvil_designer import DetailsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Data


class Details(DetailsTemplate):
  """This Form is responsible for collecting user inputs for a new ticket.
  
  The inputs are written to self.item using Data Bindings.
  """
  
  def __init__(self, **properties):
    self.agents = [(x['email'], x) for x in anvil.server.call('get_users')]
    # The category_dropdown is bound to self.categories using Data Bindings
    self.categories = Data.CATEGORIES
    # The priority_dropdown is bound to self.priorities using Data Bindings
    self.priorities = Data.PRIORITIES
    self.details = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def save_ticket_button_click(self, **event_args):
    # This calls the 'add_ticket' method on the 'Customer' Form
    self.parent.assign_customer.add_ticket(ticket=self.item, details=self.details)
    
  def set_current_no(self):
    current_no = Data.CURRENT_TICKET_NO
    return f"# {current_no['number']}"

  def cancel_button_click(self, **event_args):
    homepage = get_open_form()
    homepage.open_tickets()


