# Telegram Assistant

An assistant designed to help organize personal life matters, focusing initially on financial organization.

The assistant can:

* Record spending limits by category
* Report spending limits by category
* Edit spending limits by category
* Delete spending limits by category

* Record spending by category
* Report spending by category
* Edit spending by category
* Delete spending by category
* Alert when expenses exceed the established limit for a category

## Implemented Features

- [x] Record spending limits by category
- [x] Report spending limits by category
- [x] Edit spending limits by category
- [x] Delete spending limits by category
- [x] Record spending by category
- [ ] Report spending by category
- [ ] Edit spending by category
- [ ] Delete spending by category
- [ ] Alert when expenses exceed the limit established for the category

## Issues

- [ ] Improve the way the assistant interprets exceptions. For example, when attempting to update a category that already exists.
- [ ] Sometimes the assistant passes a simple string with special characters. Example: "farmacia" becomes "farm\303\241cia".
- [ ] Sometimes the assistant adds budget and spending without asking for all parameters. For example, updating the "farmacia" category without requesting the value and assuming a random value. One solution could be implementing a Pydantic validator before the assistant calls the database API.
