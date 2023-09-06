from ._anvil_designer import CustomerTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Validation


class Customer(CustomerTemplate):
  """This Form is responsible for linking a customer to the ticket being created on the 'Details' Form. 
  
  It either creates a new customer, or selects an existing customer.
  Keyword Arguments:
    item (optional): a row from the 'Customers' Data Table
  If initialised with an 'item' argument, this is initialised as self.selected_customer in the form_show method.
  """
  
  def __init__(self, **properties):
    self.new = True
    self.new_customer = {}
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Get customers from the server
    self.customers = anvil.server.call('get_customers')
    self.repeating_panel_results.items = []
    # Set up an event handler - this is called when a customer is selected in CustomerSearchRow
    self.repeating_panel_results.set_event_handler('x-result-selected', self.set_result)

  def new_customer_button_click(self, **event_args):
    self.new = True
    self.repeating_panel_results.items = []
    self.text_box_search.text = ""
    self.new_customer_box.visible = True

  def text_box_search_focus(self, **event_args):
    # Refresh the keys when the search box is selected, and populate the suggestions panel.
    self.text_box_search.text = ""
    self.selected_customer = {}
    self.new = False
    self.new_customer_box.visible = False
    self.populate_results(self.text_box_search.text)
  
  def text_box_search_change(self, **event_args):
    # Populate the suggestions when text is entered.
    self.populate_results(self.text_box_search.text)

  def text_box_search_pressed_enter(self, **event_args):
    # Choose the top result when enter is pressed.
    results = self.repeating_panel_results.get_components()
    if results:
      results[0].link_search_result.raise_event('click')

  def populate_results(self, text):
    # Populate the suggestions panel.
    if text == '':
      self.repeating_panel_results.items = []
    else:
      # Populate the results list
      self.repeating_panel_results.items = [
        c for c in self.customers
        if text.lower() in c['first_name'].lower()
        or text.lower() in c['last_name'].lower()
        or text.lower() in f"{c['first_name'].lower()} {c['last_name'].lower()}"
      ]

  def set_result(self, result, **event_args):
    self.selected_customer = result
    self.refresh_data_bindings()
    self.text_box_search.text = f"{result['first_name']} {result['last_name']}"
    self.repeating_panel_results.items = []
    
  def add_ticket(self, ticket, details):
    if self.new:
      customer = self.new_customer
      cust_validation_errors = Validation.get_customer_errors(customer)
    else:
      customer = self.selected_customer
      cust_validation_errors = None
      if customer == {}:
        alert("Please choose a customer")
        return
    tick_validation_errors = Validation.get_ticket_errors(ticket)
    if not cust_validation_errors and not tick_validation_errors:
      ticket = anvil.server.call('add_ticket', ticket, details, customer)
      Notification('Ticket Added').show()
      homepage = get_open_form()
      homepage.open_ticket(item=ticket)
    elif cust_validation_errors and tick_validation_errors:
      alert("The following fields are missing for your customer: \n{}.\n\nThe following field are missing for your ticket: \n{}".format(
        ' \n'.join(word.capitalize() for word in cust_validation_errors),
        ' \n'.join(word.capitalize() for word in tick_validation_errors)
      ))
    elif tick_validation_errors and not cust_validation_errors:
      alert("The following ticket fields are missing: \n{}".format(' \n'.join(word.capitalize() for word in tick_validation_errors)))
    elif cust_validation_errors and not tick_validation_errors:
      alert("The following customer fields are missing: \n{}".format(' \n'.join(word.capitalize() for word in cust_validation_errors)))

  def form_show(self, **event_args):
    if self.item:
      self.new = False
      self.selected_customer = self.item
      self.text_box_search.text = f"{self.selected_customer['first_name']} {self.selected_customer['last_name']}"


