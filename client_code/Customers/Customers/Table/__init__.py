from ._anvil_designer import TableTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import string


class Table(TableTemplate):
  """This Form is responsible for displaying Customer data, grouped by letter of the alphabet.
  
  Keyword Arguments:
    item: accepts a list of customers from the Customers Data Table (a Data Tables search iterator)
          this is passed through from the 'Customers' Form. 
          This is initialised as self.customers in the `form_refreshing_data_bindings` method
  """
  
  def __init__(self, **properties):
    self.selected_customers = []
    self.customers = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.customers_repeating_panel.set_event_handler('x-select-customer', self.select_customer)
    self.customers_repeating_panel.set_event_handler('x-deselect-customer', self.deselect_customer)
  
  # Selecting and Deselecting customers
  def select_all_box_change(self, **event_args):
    if self.select_all_box.checked:
      self.select_all()
    else:
      self.deselect_all()
  
  def select_customer(self, customer, **event_args):
    self.selected_customers.append(customer)
    self.clear_selected_link.visible = True
    
  def deselect_customer(self, customer, **event_args):
    self.selected_customers.remove(customer)
    if self.selected_customers == []:
      self.clear_selected_link.visible = False
  
  def select_all(self):
    self.selected_customers = []
    self.clear_selected_link.visible = True
    for t in self.customers_repeating_panel.get_components():
      for c in t.customers_repeating_panel.get_components():
        self.selected_customers.append(c)
        c.role = "customers-repeating-panel-selected"
        c.check_box_1.checked = True

  def deselect_all(self):
    self.selected_customers = []
    self.clear_selected_link.visible = False
    for t in self.customers_repeating_panel.get_components():
      for c in t.customers_repeating_panel.get_components():
        c.role = "customers-repeating-panel"
        c.check_box_1.checked = False

  def delete_customer_link_click(self, **event_args):
    if self.selected_customers:
      names = [f"{c['first_name']} {c['last_name']}" for c in self.selected_customers]
      if confirm("""Are you sure you want to delete these customer(s)?: \n{} 
                 \nThis will also delete all tickets associated with this customer.""".format(' \n'.join(names))):
        anvil.server.call('delete_customers', self.selected_customers)
        Notification('Customers deleted successfully').show()
        homepage = get_open_form()
        homepage.open_customers()
      else:
        self.deselect_all()
    else:
      alert("No customers selected")
      
  def form_refreshing_data_bindings(self, **event_args):
    # Populate the list of customers in the RepeatingPanel from self.item
    # self.item is a list of customers passed through from the 'Customers' Form
    if self.item and self.customers is None:
      letters = list(string.ascii_uppercase)
      self.customers = self.item
      data = []
      for let in letters:
        customers = [x for x in self.customers if x['last_name'][0].upper() == let]
        if customers:
          data.append({'letter': let, 'customers':customers})
      # Pass a dict of letters and customers to the 'LetterGroup' Form which is the ItemTemplate of customers_repeating_panel
      self.customers_repeating_panel.items = data

  def scroll_customers_letter_group(self, letter):
    # Scroll the appropriate LetterGroup on the customers_repeating_panel into view
    for letter_group in self.customers_repeating_panel.get_components():
      if letter_group.item['letter'] == letter:
        letter_group.scroll_into_view()

  def clear_selected_link_click(self, **event_args):
    self.select_all_box.checked = False
    self.deselect_all()


