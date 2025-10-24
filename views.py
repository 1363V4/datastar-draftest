from champs import champs
from models import Draft

async def home_page():
    drafts = Draft.select()
    drafts_html = []
    for draft in drafts:
        if not draft.current_move == 20:
            continue
        total_votes = draft.votes_blue + draft.votes_red
        drafts_html += [
            f'''
            <article class="gm-m">
                <div class="ratio">
                    <button data-on-click="@post('/d/{draft.id}?vote=blue')">Vote Blue</button>
                    <div>
                        <div class="blue-ratio" style="width: {100 * draft.votes_blue / total_votes}%">{round(100 * draft.votes_blue / total_votes)}%</div>
                        <div class="red-ratio" style="width: {100 * draft.votes_red / total_votes}%">{round(100 * draft.votes_red / total_votes)}%</div>
                    </div>
                    <button data-on-click="@post('/d/{draft.id}?vote=red')">Vote Red</button>
                </div>
                <div class="picks gc">
                    <div data-sheet={champs[draft.b1p]['sheet']} data-champion="{champs[draft.b1p]['name']}" aria-describedby="aria-{champs[draft.b1p]['name']}"><div id=aria-{champs[draft.b1p]['name']} role="tooltip">{champs[draft.b1p]['name']}</div></div>
                    <div data-sheet={champs[draft.b2p]['sheet']} data-champion="{champs[draft.b2p]['name']}" aria-describedby="aria-{champs[draft.b2p]['name']}"><div id=aria-{champs[draft.b2p]['name']} role="tooltip">{champs[draft.b2p]['name']}</div></div>
                    <div data-sheet={champs[draft.b3p]['sheet']} data-champion="{champs[draft.b3p]['name']}" aria-describedby="aria-{champs[draft.b3p]['name']}"><div id=aria-{champs[draft.b3p]['name']} role="tooltip">{champs[draft.b3p]['name']}</div></div>
                    <div data-sheet={champs[draft.b4p]['sheet']} data-champion="{champs[draft.b4p]['name']}" aria-describedby="aria-{champs[draft.b4p]['name']}"><div id=aria-{champs[draft.b4p]['name']} role="tooltip">{champs[draft.b4p]['name']}</div></div>
                    <div data-sheet={champs[draft.b5p]['sheet']} data-champion="{champs[draft.b5p]['name']}" aria-describedby="aria-{champs[draft.b5p]['name']}"><div id=aria-{champs[draft.b5p]['name']} role="tooltip">{champs[draft.b5p]['name']}</div></div>
                    <img src="/static/img/vs.svg"/>
                    <div data-sheet={champs[draft.r5p]['sheet']} data-champion="{champs[draft.r5p]['name']}" aria-describedby="aria-{champs[draft.r5p]['name']}"><div id=aria-{champs[draft.r5p]['name']} role="tooltip">{champs[draft.r5p]['name']}</div></div>
                    <div data-sheet={champs[draft.r4p]['sheet']} data-champion="{champs[draft.r4p]['name']}" aria-describedby="aria-{champs[draft.r4p]['name']}"><div id=aria-{champs[draft.r4p]['name']} role="tooltip">{champs[draft.r4p]['name']}</div></div>
                    <div data-sheet={champs[draft.r3p]['sheet']} data-champion="{champs[draft.r3p]['name']}" aria-describedby="aria-{champs[draft.r3p]['name']}"><div id=aria-{champs[draft.r3p]['name']} role="tooltip">{champs[draft.r3p]['name']}</div></div>
                    <div data-sheet={champs[draft.r2p]['sheet']} data-champion="{champs[draft.r2p]['name']}" aria-describedby="aria-{champs[draft.r2p]['name']}"><div id=aria-{champs[draft.r2p]['name']} role="tooltip">{champs[draft.r2p]['name']}</div></div>
                    <div data-sheet={champs[draft.r1p]['sheet']} data-champion="{champs[draft.r1p]['name']}" aria-describedby="aria-{champs[draft.r1p]['name']}"><div id=aria-{champs[draft.r1p]['name']} role="tooltip">{champs[draft.r1p]['name']}</div></div>
                </div>
                <div class="ban-wrapper bans">
                    <div data-sheet={champs[draft.b1b]['sheet']} data-champion="{champs[draft.b1b]['name']}"></div>
                    <div data-sheet={champs[draft.b2b]['sheet']} data-champion="{champs[draft.b2b]['name']}"></div>
                    <div data-sheet={champs[draft.b3b]['sheet']} data-champion="{champs[draft.b3b]['name']}"></div>
                    <div data-sheet={champs[draft.b4b]['sheet']} data-champion="{champs[draft.b4b]['name']}"></div>
                    <div data-sheet={champs[draft.b5b]['sheet']} data-champion="{champs[draft.b5b]['name']}"></div>
                    <div></div>
                    <div data-sheet={champs[draft.r5b]['sheet']} data-champion="{champs[draft.r5b]['name']}"></div>
                    <div data-sheet={champs[draft.r4b]['sheet']} data-champion="{champs[draft.r4b]['name']}"></div>
                    <div data-sheet={champs[draft.r3b]['sheet']} data-champion="{champs[draft.r3b]['name']}"></div>
                    <div data-sheet={champs[draft.r2b]['sheet']} data-champion="{champs[draft.r2b]['name']}"></div>
                    <div data-sheet={champs[draft.r1b]['sheet']} data-champion="{champs[draft.r1b]['name']}"></div>
                </div>
            </article>
            '''
        ]
    html = f'''
<div id="drafts">
{"".join(drafts_html)}
</div>
    '''
    return html

async def draft_page(draft_id, user_id):
    draft = Draft.get(Draft.id == draft_id)
    instruction, alert = "", ""
    blue_view = str(draft.blue).replace("-", "") == user_id
    match draft.current_move:
        case 1 | 2 | 5 | 13 | 14:
            instruction = "Red ban"
            alert = "Wait for opponent to play" if blue_view else ""
        case 0 | 3 | 4 | 12 | 15:
            instruction = "Blue ban"
            alert = "Wait for opponent to play" if not blue_view else ""
        case 6 | 9 | 10 | 17 | 18:
            instruction = "Blue pick"
            alert = "Wait for opponent to play" if blue_view else ""
        case 7 | 8 | 11 | 16 | 19:
            instruction = "Red pick"
            alert = "Wait for opponent to play" if not blue_view else ""
        case _:
            instruction = "GG"
    if not draft.red:
        alert = f'''
        Send this link to the other player:
        <hr class="gm-s">
        https://draft.leg.ovh/d/{draft.id}
        '''
    if draft.blue == draft.red:
        alert = ""
    all_champs = [
        draft.b1p, draft.b1b, draft.b2p, draft.b2b, draft.b3p, 
        draft.b3b, draft.b4p, draft.b4b, draft.b5p, draft.b5b, 
        draft.r1p, draft.r1b, draft.r2p, draft.r2b, draft.r3p, 
        draft.r3b, draft.r4p, draft.r4b, draft.r5p, draft.r5b
    ]
    the_chefs_trick = {'sheet': -1, 'name': 'MissingNo'}
    instruction_class = ""
    if "Blue" in instruction:
        instruction_class = "blue-instruction"
    elif "Red" in instruction:
        instruction_class = "red-instruction"
    
    html = f'''
<body class="gc">
<p id="instructions" class="gt-xl {instruction_class}">{instruction}</p>
{f'<div class="go gp-m alert">{alert}</div>' if alert else ""}
<div id="wrapper">
    <article id="blue-side" class="gc">
        <div class="draft-header blue-header">BLUE DRAFT</div>
        <div class="bans" data-sheet={champs.get(draft.b1b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b1b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b1p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b1p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.b2b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b2b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b2p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b2p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.b3b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b3b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b3p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b3p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.b4b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b4b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b4p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b4p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.b5b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b5b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b5p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b5p, the_chefs_trick)['name']}"></div>
    </article>
    <article id ="picker"
    data-signals-filter__ifmissing="'all'"
    >
        <div id="roles">
            <div class="gz gc" aria-describedby="aria-top" data-on-click="$filter == 'top' ? $filter = 'all' : $filter = 'top'" data-attr-selected="$filter == 'top'">
                <img alt="top" src="/static/img/top.webp">
                <div id=aria-top role="tooltip">Top</div>
            </div>
            <div class="gz gc" aria-describedby="aria-jungle" data-on-click="$filter == 'jun' ? $filter = 'all' : $filter = 'jun'" data-attr-selected="$filter == 'jun'">
                <img alt="jungle" src="/static/img/jungle.webp">
                <div id=aria-jungle role="tooltip">Jungle</div>
            </div>
            <div class="gz gc" aria-describedby="aria-mid" data-on-click="$filter == 'mid' ? $filter = 'all' : $filter = 'mid'" data-attr-selected="$filter == 'mid'">
                <img alt="mid" src="/static/img/mid.webp">
                <div id=aria-mid role="tooltip">Mid</div>
            </div>
            <div class="gz gc" aria-describedby="aria-adc" data-on-click="$filter == 'adc' ? $filter = 'all' : $filter = 'adc'" data-attr-selected="$filter == 'adc'">
                <img alt="adc" src="/static/img/adc.webp">
                <div id=aria-adc role="tooltip">ADC</div>
            </div>
            <div class="gz gc" aria-describedby="aria-supp" data-on-click="$filter == 'sup' ? $filter = 'all' : $filter = 'sup'" data-attr-selected="$filter == 'sup'">
                <img alt="supp" src="/static/img/supp.webp">
                <div id=aria-supp role="tooltip">Support</div>
            </div>
            <div></div>
            <input data-bind-search type="text" placeholder="Search"></input>
        </div>
        <div id="legends" 
        {f'''data-on-click="@post('/d/{draft.id}?pick=' + event.target.id)"''' if not alert else ""}
        >
            {"".join(
                [
                    f'''
                    <div 
                    id="{key}" 
                    data-sheet={champ['sheet']}
                    data-champion="{champ['name']}"
                    {"banned" if key in all_champs else ""}
                    data-show="($filter == 'all' || $filter == {'|| $filter == '.join(f"'{role}'" for role in champ['role'])}) 
                    && ($search == '' || '{champ['name']}'.toLowerCase().includes($search.toLowerCase()))"
                    aria-describedby="aria-{champ['name']}"
                    >'''
                    + f'<div id=aria-{champ['name']} role="tooltip">{champ['name']}</div></div>'
                    for key, champ in champs.items()
                ]
            )}
        </div>
    </article>
    <article id="red-side" class="gc">
        <div class="draft-header red-header">RED DRAFT</div>
        <div data-sheet={champs.get(draft.r1p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r1p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.r1b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r1b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r2p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r2p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.r2b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r2b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r3p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r3p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.r3b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r3b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r4p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r4p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.r4b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r4b, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r5p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r5p, the_chefs_trick)['name']}"></div>
        <div class="bans" data-sheet={champs.get(draft.r5b, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r5b, the_chefs_trick)['name']}"></div>
    </article>
</div>
</body>
'''
    return html