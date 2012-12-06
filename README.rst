django-comment-plus
===================

Extended version of django.contrib.comments

Features
---------

* Keep comments and reviews (different from the comment field "is_review" and the type of review, such as "positive"/"negative");
* Anonymous users can enter "email", "name" and a comment, then comment send to pre-moderated queue and user making a registred user on the site and send a letter to confirm. This way the user will remain anonymous, but will become a registered user;
* Form on ajax, essentially only form validation errors are displayed, and after a successful submission is redirected, I think it is necessary to translate the full ajax;
* Subscribe to the comments and sending letters to subscribers respectively. All subscriptions come with a link to "Usubscribe" in letters, also has a web interface to unsubscribe.


TODO
------

* The complete code coverage of tests;
* Branching of the comment list.