# Todo
rest of the champs DONE
uh oh je redraft à chaque refresh FIX aux query strings
Order is wrong. How to do selected??
Add bans (change 10 to 20)
Vote on drafts (change db)
Vs IA and vs someone else OK 
CSS fix (background text) OK
Leaky bucket OK
Put online?

# Notes
bottleneck for now seems to be redis pubsub
we do shell+stream 2 times for easier pubsub deco/reco

# En fait
pubsub sur la draft est overkill
et si je leaky bucket pourquoi besoin d'async
alors que je peux faire un 10FPS serveur en sync
Process input, update game, render/draw
read-eval-print
Zero cookie use aussi à part user_id
On garde l'info, on fait des routes hypermedia
Pas trop de routes, get/post differentiation, query string and match

# Next
Les gens veulent
Authentication, security tokens, CORS, CSRF, XSS