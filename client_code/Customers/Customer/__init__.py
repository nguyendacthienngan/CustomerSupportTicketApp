from ._anvil_designer import CustomerTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ... import Validation


class Customer(CustomerTemplate):
  """This Form is responsible for editing customer information. 
  
  It is added to the 'Overlay' slot on the 'Homepage' Form, 
  which overlays it on top of the Form in the 'default' slot on the Homepage.
  It has a click handler on the 'grey' section of the overlay, which removes the overlay to reveal the content underneath. 
  This is trigged by JavaScript on the 'three_slot_overlay.html' asset, which calls the 'clear_overlay' method on this Form, from JavaScript.
  
  Keyword arguments:
    item - accepts a row from the customers data table
           Initialises this in the 'refresh_data' method.
  """
  
  def __init__(self, **properties):
    self.customer_copy = {}
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.refresh_data()
    
  def refresh_data(self):
    """Set self.customer_copy to the original customer, stored in self.item"""
    self.customer_copy = dict(list(self.item))
    self.refresh_data_bindings()

  def cancel_link_click(self, **event_args):
    # If the edit operation is cancelled, reset the changes to customer_copy and return to the Customer view 
    self.refresh_data()
    self.clear_overlay()

  def save_button_click(self, **event_args):
    # Return validation errors from the Validation module
    cust_validation_errors = Validation.get_customer_errors(self.customer_copy)
    if not cust_validation_errors:
      anvil.server.call('update_customer', self.item, self.customer_copy)
      Notification('Customer details updated').show()
      homepage = get_open_form()
      homepage.open_customer(self.item)    
    else:
      alert("The following fields are missing for your customer: \n{}".format(
        ' \n'.join(cust_validation_errors)
      ))
  
  def clear_overlay(self):
    """This is called from the JavaScript on the `three_slot_overlay.html` asset"""
    homepage = get_open_form()
    homepage.close_overlay()
    

      
      
      
      
      
      
      
      
      
      
      
