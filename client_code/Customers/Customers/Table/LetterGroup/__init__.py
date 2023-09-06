from ._anvil_designer import LetterGroupTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class LetterGroup(LetterGroupTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'Table' Form
  
  It displays a single letter from the alphabet in letter_label via data bindings
  It then sends a list of customers whose name begins with the letter in letter_label to the 'CustomerRow' Form.
  
  Keyword Arguments:
    item: accepts a dict in the form {'letter': let, 'customers':customers}
          'let' is a list of letters and 'customers' is a list of customer rows from the customers data table. 
          'customers' is a list of customers passed through from the 'Table' Form. 
           The 'items' property of the customers_repeating_panel is set to self.item['customers'] using Data Bindings
  """
  
  def __init__(self, **properties):
     # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.customers_repeating_panel.set_event_handler('x-select-customer', self.select_customer)
    self.customers_repeating_panel.set_event_handler('x-deselect-customer', self.deselect_customer)
    
  def select_customer(self, customer, **event_args):
    self.parent.raise_event('x-select-customer', customer=customer)
    
  def deselect_customer(self, customer, **event_args):
    self.parent.raise_event('x-deselect-customer', customer=customer)