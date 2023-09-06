from ._anvil_designer import MessageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ..... import Data


class Message(MessageTemplate):
  
  """This is the ItemTemplate of the RepeatingPanel on the 'Info' Form. It displays data for a single message"""
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
  def set_to_labels(self):
    """Populates the to_label with the appropriate data using Data Bindings"""
    if self.item['type'] == Data.INTERNAL:
      return "[INTERNAL NOTE]"
    elif self.item['type'] == Data.INCOMING:
      return "To: Support"
    else:
      return f"To: {self.item['ticket']['customer']['first_name']} {self.item['ticket']['customer']['last_name']}"

  def set_from_labels(self):
    """Populates the from_label with the appropriate data using Data Bindings"""
    if self.item['type'] == Data.INCOMING:
      return f"From: {self.item['ticket']['customer']['first_name']} {self.item['ticket']['customer']['last_name']}"
    else:
      return f"From: {self.item['agent']['email']}"
