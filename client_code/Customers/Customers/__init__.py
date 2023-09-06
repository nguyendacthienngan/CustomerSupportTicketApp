from ._anvil_designer import CustomersTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import string


class Customers(CustomersTemplate):
  """This Form displays a list of Customers from the 'customers' Data Table, grouped by letter of the alphabet.
  
  It also displays a list of the letters of the alphabet.
  It fetches a list of customers from the server, and passes them to the 'Table' Form via Data Bindings.
  """
  
  def __init__(self, **properties):
    self.customers = anvil.server.call('get_customers')
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.letters_repeating_panel.set_event_handler('x-scroll-letter', self.scroll_letter)

    # Any code you write here will run when the form opens.
    letters = list(string.ascii_uppercase)
    data = []
    for let in letters:
      # Group all our customers by letter of the alphabet
      customers = [x for x in self.customers if x['last_name'][0].upper() == let]
      if customers:
        data.append({'letter': let, 'customers':customers})
    
    # Work out which letters of the alphabet should be visible
    # Don't show letters if none of our customers' surnames begin with that letter
    visible_letters = [x['letter'] for x in data]
    letters = [{
        'letter': x,
        'visible': x in visible_letters
      } for x in string.ascii_uppercase]
    
    self.letters_repeating_panel.items = letters
    
  def scroll_letter(self, letter, **event_args):
    # This event is raised on the 'Letter' Form
    # Call the `scroll_customers_letter_group` method on the 'Table' Form
    self.customer_table.scroll_customers_letter_group(letter)
    
    