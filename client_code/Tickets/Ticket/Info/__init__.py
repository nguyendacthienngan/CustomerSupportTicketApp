from ._anvil_designer import InfoTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Validation
from .... import Data
from datetime import date


class Info(InfoTemplate):
  """This Form is responsible for fetching messages for a single ticket, deleting a ticket and adding messages to a ticket.
  
  Keyword Arguments:
    item: a row from the 'Tickets' Data Table
  
  This row from the 'Tickets' table is initialised as self.ticket in form_refreshing_data_bindings()
  """
  
  def __init__(self, **properties):
    # self.messages:
    # 1) None means messages haven't been loaded,
    # 2) empty list means there are 0 messages for this ticket
    # initialise self.messages as None to mark that messages need fetching for this ticket
    self.messages = None
    self.message = {}
    self.ticket = {}
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
  def delete_ticket_button_click(self, **event_args):
    if confirm(f"Are you sure you want to delete: \n{self.item['title']}?"):
      # Delete tickets expects a list of tickets so pass self.item as a list 
      anvil.server.call('delete_tickets', [self.item])
      homepage = get_open_form()
      homepage.open_tickets()
    
  def set_overdue_closed_label(self):
    if self.item['status'] == Data.CLOSED:
      self.overdue_label.text = "CLOSED"
      self.overdue_label.foreground = "#25D89D"
      self.overdue_label.visible = True
    elif self.item['due'] < date.today():
      self.overdue_label.text = "OVERDUE"
      self.overdue_label.foreground = "#FF5658"
      self.overdue_label.visible = True
    else:
      self.overdue_label.visible = False
 
  
  def populate_messages(self):
    # Fetch messages for this ticket from the server
    self.messages = anvil.server.call('get_messages', self.item)
    self.messages_repeating_panel.items = self.messages
    
  def populate_to_dropdown(self):
    INTERNAL = Data.INTERNAL
    OUTGOING = Data.OUTGOING
    # Populate values of the to_dropdown
    self.to_dropdown.items = [
      (f"{self.item['customer']['first_name']} {self.item['customer']['last_name']}", OUTGOING), 
      ('Internal Note', INTERNAL)
    ]
    self.message['type'] = OUTGOING

  def form_refreshing_data_bindings(self, **event_args):
    # If messages haven't been fetched for this ticket yet, fetch them
    if self.messages is None and self.item:
      self.populate_messages()
      self.populate_to_dropdown()
    # If self.ticket hasn't been initialised yet, initialise it
    if self.ticket == {} and self.item:
      self.ticket = self.item
      if self.item['due'] < date.today() or self.item['status'] == Data.CLOSED:
        self.set_overdue_closed_label()

  def reply_button_click(self, **event_args):
    self.ticket_reply.visible = True
    self.ticket_reply.scroll_into_view()
        
  def send_reply_button_click(self, **event_args):
    # Return any validation errors for the message being created
    message_validation_errors = Validation.get_message_errors(self.message)
    if not message_validation_errors:
      self.reply_details_box.text = ""
      self.ticket_reply.visible = False
      anvil.server.call('add_message', self.message, self.item)
      Notification('Reply added').show()
      self.populate_messages()
    else:
      alert("\nThe following field are missing for your reply: \n{}".format(
        ' \n'.join(message_validation_errors)
      ))
    
  def cancel_reply_button_click(self, **event_args):
    self.reply_details_box.text = ""
    self.ticket_reply.visible = False
    
  def scroll_reply_box(self):
    self.reply_details_box.scroll_into_view()
    
    
  

