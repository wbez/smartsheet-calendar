# Smartsheet Calendar
Simple app that takes a smartsheet with a list of show segments and lists them out by day, with the current day in the middle of a five-day week. Assumes your smartsheet has columns ```Show | Status | Air Date | Story Slug | Segment Type | Reporter | Category1 | Category2.```

Uses flask as the app framework and the smartsheet python api to pull in information.