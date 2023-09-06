from ._anvil_designer import HomepageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objs as go
from ..Tickets.Tickets import Tickets
from ..Dashboard import Dashboard
from ..Tickets.Ticket import Ticket
from ..Customers.Customers import Customers
from ..Customers.Customer import Customer
from ..Customers.CustomerDetailsOverlay import CustomerDetailsOverlay
from ..Tickets.NewTicket import NewTicket


class Homepage(HomepageTemplate):
  """This Form controls navigation for the whole app.
  
  It has two "slots" that accept Anvil components, named 'default', and 'overlay'.
  Navigation works by loading Forms into this Form's "default" slot.
  
  The "overlay" slot is used by certain Forms to 'overlay' themselves
  on top of the content currently displayed in the "default" slot on the Hompage. 
  """

  def __init__(self, **properties):
    # Is the 'Ticket' Form currently open? - set default to False
    self.ticket_form_open = False
    # Is the 'Customers' Form currently open? - set default to False
    self.customers_form_open = False
  
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if anvil.users.get_user():
      self.open_dashboard()

  def open_dashboard(self):
    """Open the 'Dashboard' Form, by adding it to the "default" slot."""
    self.dash_panel.role = 'dash-link-selected'
    self.headline_label.text = "Dashboard"
    self.current_form = Dashboard()
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_tickets(self, initial_filters={}, initial_date_filters={}):
    """Open the 'Tickets' Form, by adding it to the "default" slot.
    
    Arguments:
      initial_filters - can be passed through to instantiate 
                        the 'Tickets' Form with filters already in place.
                        e.g initial_filters={'status': Data.OPEN} to show all unresolved Tickets.
      initial_date_filters - as with initial_filters, but for dates.
    """
    self.current_form = Tickets(initial_filters, initial_date_filters)
    self.ticket_panel.role = 'dash-link-selected'
    self.headline_label.text = "Tickets"
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_ticket(self, item):
    """Open the 'Ticket' Form, by adding it to the "default" slot.

    Argments:
      item - a row from the 'Tickets' Data Table
    """
    if self.ticket_form_open:
      # If the current view is the 'Ticket' Form, only refresh items that need refreshing
      self.current_form.ticket_copy = dict(list(item))
      self.current_form.item = item
      print(self.current_form.ticket_copy.items())
#       print(dir(self.current_form))
#       print(dir(self.current_form.ticket_copy))
      self.current_form.ticket.populate_messages()
    else:
      self.ticket_form_open = True
      self.ticket_panel.role = 'dash-link-selected'
      self.headline_label.text = "Tickets"
      self.current_form = Ticket(item=item)
      self.clear_page()
      self.add_component(self.current_form, slot="default")
  
  def open_new_ticket_form(self, initial_customer={}):
    """Open the 'NewTicket' Form, by adding it to the "default" slot.
    
    Argments:
      initial_customer - Can be passed in to create a ticket for a specific customer. 
                         Expects a row from the Customers Data Table
    """
    self.ticket_panel.role = 'dash-link-selected'
    self.headline_label.text = "Tickets"
    self.current_form = NewTicket(initial_customer)
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_customers(self):
    """Open the 'Customers' Form, by adding it to the "default" slot."""
    self.customers_form_open = True
    self.customer_panel.role = 'dash-link-selected'
    self.headline_label.text = "Customers"
    self.current_form = Customers()
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_customer(self, item):
    """Open the 'Customer' Form, by adding it to the "overlay" slot.
    
    Arguments: 
      item - a row from the 'Customers' Data Table.
    """
    # If the 'Customers' Form is currently open in the "default" slot on the Homepage,
    # don't reload it, just replace the Form in the "overlay" slot
    if self.customers_form_open:
      self.clear(slot="overlay")
      self.add_component(CustomerDetailsOverlay(item=item), slot="overlay")
    else:
      self.customer_panel.role = 'dash-link-selected'
      self.headline_label.text = "Customers"
      self.current_form = Customers()
      self.clear_page()
      self.add_component(self.current_form, slot="default")
      self.add_component(CustomerDetailsOverlay(item=item), slot="overlay")
  
  def add_customer_edit_overlay(self, item):
    """Open the 'CustomerDetailOverlay' Form, by adding it to the "overlay" slot.
    
    Arguments:
      item - a row from the 'Customers' Data Table.
    """
    self.add_component(Customer(item=item), slot="overlay")
    
  def dash_link_click(self, **event_args):
    # Open the dashboard when the dash_link is clicked
    self.open_dashboard()
    
  def ticket_link_click(self, **event_args):
    # Open the ticket inbox when the ticket_link is clicked
    self.open_tickets()
  
  def customer_link_click(self, **event_args):
    # Open the customers view when the customer_link is clicked
    self.open_customers()

  def new_ticket_button_click(self, **event_args):
    # Open the NewTicket Form when the new_ticket_button is clicked
    self.open_new_ticket_form()

  def clear_page(self):
    self.ticket_form_open = False
    self.customers_form_open = False
    # Clear both slots
    self.clear(slot="overlay")
    self.clear(slot="default")
    # Reset links in the links_panel so they are not highlighted
    for panel in self.links_panel.get_components():
      panel.role = "dash-link"
      
  def close_overlay(self):
    """Clear the 'Overlay' slot."""
    self.clear(slot="overlay")
    
  def signout_link_click(self, **event_args):
    anvil.users.logout()
    open_form('Login')

  def form_show(self, **event_args):
    if anvil.users.get_user() is None:
      open_form('Login')
      






