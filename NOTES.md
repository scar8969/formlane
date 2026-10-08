== curl ==
# POST /f/a8f2k3  -H "Content-Type: application/json"  {"name":"Alice","email":"alice@example.com","message":"hi"}
# GET  /api/forms
# POST /api/forms  {"name":"contact","deliver":{"email":"ops@me.com"},"spam":{"honeypot":true,"rate":5}}
# GET  /api/forms/1/submissions

== session plan ==
# Session 1: endpoints + spam (honeypot/rate/keyword) → tests
# Session 2: deliver (email debug SMTP + webhook mock) → tests
# Session 3: web templates + screenshots → README → CI/Docker/Pages → tag
