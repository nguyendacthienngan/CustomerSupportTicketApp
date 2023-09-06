"""This module collects global variables to be used throughout the app"""
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


CATEGORIES = [(x['name'], x) for x in app_tables.categories.search()]
PRIORITIES = [(x['name'], x) for x in app_tables.priorities.search()]
STATUS = [(x['name'], x) for x in app_tables.status.search()]
OPEN = app_tables.status.get(name="Open")
URGENT = app_tables.priorities.get(name="Urgent")
CLOSED = app_tables.status.get(name="Closed")
OUTGOING = app_tables.types.get(name="OUTGOING_EMAIL")
INTERNAL = app_tables.types.get(name="INTERNAL_NOTE")
INCOMING = app_tables.types.get(name="INCOMING_EMAIL")
CURRENT_TICKET_NO = app_tables.currentticketno.search()[0]
NO_AGENTS_SELECTED = 'None'
NEW_CATEGORY = app_tables.categories.get(name="New")
NEW_PRIORITY = app_tables.priorities.get(name="New")