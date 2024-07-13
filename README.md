# Telegram Assistent

Assistant that helps to organize personal life stuffs. In the first moment the focus of this project will be the financial organization.

The assistant will be able to do:

* Record spending limit by category
* Report spending limit by category
* Edit spending limit by category
* Delete spending limit by category

* Record spending by category
* Report spending by category
* Edit spending by category
* Delete spending by category
* Alert if expenses exceed the limit established for the category


## Implemented Features

- [x] Record spending limit by category
- [x] Report spending limit by category
- [x] Edit spending limit by category
- [x] Delete spending limit by category
- [x] Record spending by category
- [ ] Report spending by category
- [ ] Edit spending by category
- [ ] Delete spending by category
- [ ] Alert if expenses exceed the limit established for the category


## Issues

- [ ] Improve the way that LLM interpret exceptions. For example: When I try to update a category that already exists.
- [ ] Sometimes LLM is passing a simple string with special character. Example: farmacia -> farm\303\241cia
- [ ] Sometimes LLM is add budget and spent without asking all parameters. Example: LLM is updating "farmacia" category without asking me the value and is assuming a random value. A idea to solve it will be to implement a pydantic validator before agent call the database api.


