import asyncio
from datetime import datetime
import redis.asyncio as redis
import logging
from uuid import uuid4

from sanic import Sanic, html, redirect
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

from peewee import SqliteDatabase

from views import home_page, draft_page
from models import Draft
from move_order import move_order


leaky_q = asyncio.Queue()
LEAKY_OUT = 5
LEAKY_EVERY = 0.01

app = Sanic(__name__)
app.static('/static/', './static/')
app.static('/', './index.html', name="index")

app.update_config({'RESPONSE_TIMEOUT': 60*10})

logging.basicConfig(filename='perso.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.before_server_start
async def open_connections(app):
    app.ctx.db = SqliteDatabase('drafts.db')
    app.ctx.db.bind([Draft])
    app.ctx.db.connect()
    with app.ctx.db:
        app.ctx.db.create_tables([Draft])
    app.ctx.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.after_server_stop
async def close_connections(app):
    app.ctx.db.close()
    await app.ctx.redis_client.aclose()

@app.on_response
async def cookie(request, response):
    if not request.cookies.get("user_id"):
        user_id = uuid4().hex
        response.add_cookie('user_id', user_id)

@app.get("/home_updates")
@datastar_response
async def home_updates(request):
    pubsub = app.ctx.redis_client.pubsub()
    await pubsub.subscribe("main")
    try:
        async for _ in pubsub.listen():
            print(datetime.now())
            response_html = await home_page()
            print(datetime.now())
            yield SSE.patch_elements(response_html)
    except asyncio.CancelledError:
        raise
    finally:
        await pubsub.unsubscribe("main")
        await pubsub.close()

@app.get("/draft")
async def new_draft(request):
    user_id = request.cookies.get('user_id')
    draft_id = Draft.create(
        red=user_id,
        blue=user_id
    )
    return redirect(f"/d/{draft_id}")

@app.get("/d/<draft_id>")
async def draft(request, draft_id):
    return html(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draftest</title>
    <link rel="icon" href="/static/img/rocket.png">
    <link rel="stylesheet" href="/static/css/site.css">
    <script type="module" src="/static/js/datastar.js"></script>
</head>
<body class="gc">
    <h1 class="gt-xl gm-xl">LOL Drafts</h1>
    <div id="drafts" class="gc" data-on-load="@get('/d/{draft_id}/draft_updates')">
        <span class="loader"></span>
        <p>Preparing your draft</p>
    </div>
</body>
</html>
    ''')

@app.get("/d/<draft_id>/draft_updates")
@datastar_response
async def draft_updates(request, draft_id):
    user_id = request.cookies.get('user_id')
    pubsub = app.ctx.redis_client.pubsub()
    channel = f"draft:{draft_id}"
    await pubsub.subscribe(channel)
    try:
        async for msg in pubsub.listen():
            print(datetime.now(), msg)
            response_html = await draft_page(draft_id, user_id)
            yield SSE.patch_elements(response_html)
    except asyncio.CancelledError:
        raise
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

@app.post("/d/<draft_id>")
@datastar_response
async def da_post_route(request, draft_id):
    vote = request.args.get("vote")
    champ = request.args.get("pick")
    draft = Draft.get(Draft.id == draft_id)
    match vote, champ:
        case _, None:
            draft.votes_blue += 1
            await app.ctx.redis_client.publish("main", "rugpull")
        case None, _:
            if draft.current_move == 20:
                return
            key = move_order.get(draft.current_move)
            setattr(draft, key, champ)
            draft.current_move += 1
            draft.save()
            if draft.current_move == 20:
                await app.ctx.redis_client.publish("main", "rugpull")
            await app.ctx.redis_client.publish(f"draft:{draft_id}", "rugpull")
        case _:
            return


if __name__ == "__main__":
    app.run(debug=True, auto_reload=True, access_log=False)
