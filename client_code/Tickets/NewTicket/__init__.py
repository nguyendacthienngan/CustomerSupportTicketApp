from ._anvil_designer import NewTicketTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class NewTicket(NewTicketTemplate):
  """This Form loads the 'Customer' and 'Details' Forms that are used to create a new ticket. 
  
  Keyword Arguments:
    initial_customer (optional): a row from the 'Customers' Data Table
  If initialised with an 'initial_customer' argument, 
  it passes the customer row to the 'Details' Form as self.customer using Data Bindings
  """
  
  def __init__(self, initial_customer=None, **properties):
    self.customer = initial_customer
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
