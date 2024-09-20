def calendar_configuration():
    calendar_options = {
        "editable": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "resourceTimelineDay",
        "resourceGroupField": "building",
        "resources": [
            {"id": "a", "building": "Building A", "title": "Building A"},
            {"id": "b", "building": "Building A", "title": "Building B"},
            {"id": "c", "building": "Building B", "title": "Building C"},
            {"id": "d", "building": "Building B", "title": "Building D"},
            {"id": "e", "building": "Building C", "title": "Building E"},
            {"id": "f", "building": "Building C", "title": "Building F"},
        ],
    }
    custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """
    return calendar_options, custom_css
