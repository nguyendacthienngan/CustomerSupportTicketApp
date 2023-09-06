from ._anvil_designer import HeadlineStatsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ... import Data


class HeadlineStats(HeadlineStatsTemplate):
  """This 'HeadlineStats' custom component accepts 'value', 'delta' and 'time_period' properties will take care of its own display
  
  Component properties:
    value - string: value to be displayed
    delta - string: delta vs. previous time period
    time_period - string: time period for data being displayed (in days)
  """
  
  def __init__(self, **properties):
    self._my_time_period = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
  @property
  def value(self):
    return self.value_label.text

  @value.setter
  def value(self, value):
    self.value_label.text = value
    
  @property
  def title(self):
    return self.title_link.text

  @title.setter
  def title(self, value):
    self.title_link.text = value
    
  @property
  def delta(self):
    return self.delta_label.text

  @delta.setter
  def delta(self, value):
    if value == 0:
      self.delta_label.text = "Unchanged"
      self.role = ""
      self.delta_label.icon = None
      self.delta_label.role = ""
    else:
      self.delta_label.text = value if value > 0 else -value
      self.delta_label.icon = "fa:arrow-up" if value > 0 else "fa:arrow-down"
      self.role = "dash-up" if value > 0 else "dash-down"
      self.delta_label.role = "dash-up" if value > 0 else "dash-down"
    
  @property
  def time_period(self):
    return self._my_time_period

  @time_period.setter
  def time_period(self, value):
    self._my_time_period = value
    self.time_period_label.text = " vs previous " + value + " days"

  def title_link_click(self, sender, **event_args):
    # This raises an event on the parent `flow_panel_headline_stats`
    self.parent.raise_event('x-open-tickets', title=self.title_link.text)
    
      

