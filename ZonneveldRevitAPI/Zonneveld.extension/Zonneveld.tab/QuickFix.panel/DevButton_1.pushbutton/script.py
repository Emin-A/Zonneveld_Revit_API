# -*- coding: utf-8 -*-
__title__ = "Debug Document Changes"
__doc__ = """Debug the DocumentChanged event for workset assignment."""

from Autodesk.Revit.DB import BuiltInParameter, ElementId

# Initialize Revit document and application
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document


def document_changed_handler(doc, sender, args):
    """Handle document changes."""
    try:
        print("DocumentChanged event triggered!")
        added_elements = args.GetAddedElementIds()
        modified_elements = args.GetModifiedElementIds()
        deleted_element_ids = args.GetDeletedElementIds()

        # Log added elements
        if added_elements:
            print("Added elements count: {}".format(len(added_elements)))
            for elem_id in added_elements:
                element = doc.GetElement(elem_id)
                if element:
                    print("Added element ID: {}".format(elem_id))

        # Log modified elements
        if modified_elements:
            print("Modified elements count: {}".format(len(modified_elements)))
            for elem_id in modified_elements:
                print("Modified element ID: {}".format(elem_id))

        # Log deleted elements
        if deleted_element_ids:
            print("Deleted elements count: {}".format(len(deleted_element_ids)))
            for elem_id in deleted_element_ids:
                print("Deleted element ID: {}".format(elem_id))

    except Exception as e:
        print("Error in DocumentChanged handler: {}".format(e))


def initialize_event_handler(doc):
    """Initialize and attach the DocumentChanged event handler."""
    app = __revit__.Application
    try:
        print("Attaching DocumentChanged event handler...")
        app.DocumentChanged += lambda sender, args: document_changed_handler(
            doc, sender, args
        )
        print("Event handler attached successfully.")
    except Exception as e:
        print("Failed to attach event handler: {}".format(e))


# Initialize event handler
initialize_event_handler(doc)
