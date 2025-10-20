from champs import champs
from models import Draft

async def home_page():
    drafts = Draft.select()
    drafts_html = []
    for draft in drafts:
        if not draft.current_move == 10:
            continue
        drafts_html += [
            f'''
            <article data-on-mousedown="location.href='/draft/{draft.id}.html'">
                <div data-sheet={champs[draft.b1p]['sheet']} data-champion="{champs[draft.b1p]['name']}"></div>
                <div data-sheet={champs[draft.b2p]['sheet']} data-champion="{champs[draft.b2p]['name']}"></div>
                <div data-sheet={champs[draft.b3p]['sheet']} data-champion="{champs[draft.b3p]['name']}"></div>
                <div data-sheet={champs[draft.b4p]['sheet']} data-champion="{champs[draft.b4p]['name']}"></div>
                <div data-sheet={champs[draft.b5p]['sheet']} data-champion="{champs[draft.b5p]['name']}"></div>
                <img src="/static/img/vs.svg"/>
                <div data-sheet={champs[draft.r5p]['sheet']} data-champion="{champs[draft.r5p]['name']}"></div>
                <div data-sheet={champs[draft.r4p]['sheet']} data-champion="{champs[draft.r4p]['name']}"></div>
                <div data-sheet={champs[draft.r3p]['sheet']} data-champion="{champs[draft.r3p]['name']}"></div>
                <div data-sheet={champs[draft.r2p]['sheet']} data-champion="{champs[draft.r2p]['name']}"></div>
                <div data-sheet={champs[draft.r1p]['sheet']} data-champion="{champs[draft.r1p]['name']}"></div>
            </article>
            '''
        ]
    html = f'''
<div id="drafts">
{"".join(drafts_html)}
</div>
    '''
    return html

async def draft_page(draft_id):
    draft = Draft.get(Draft.id == draft_id)
    the_chefs_trick = {'sheet': -1, 'name': 'MissingNo'}
    html = f'''
<body class="gc">
<p id="instructions" class="gt-xl">Step 1: rug pull </p>
<p>draft {draft.id} move {draft.current_move}</p>
<div id="wrapper">
    <article id ="blue-side" class="gc">
        <div data-sheet={champs.get(draft.b1p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b1p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b2p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b2p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b3p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b3p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b4p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b4p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.b5p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.b5p, the_chefs_trick)['name']}"></div>
    </article>
    <article id ="picker"
    data-signals-filter__ifmissing="'all'"
    >
        <div id="roles">
            <img alt="top" src="/static/img/top.webp" 
            data-on-click ="$filter == 'top' ? $filter = 'all' : $filter = 'top'" 
            data-attr-selected="$filter == 'top'">
            <img alt="jungle" src="/static/img/jungle.webp" data-on-click="$filter == 'jun' ? $filter = 'all' : $filter = 'jun'" data-attr-selected="$filter == 'jun'">
            <img alt="mid" src="/static/img/mid.webp" data-on-click="$filter == 'mid' ? $filter = 'all' : $filter = 'mid'" data-attr-selected="$filter == 'mid'">
            <img alt="adc" src="/static/img/adc.webp" data-on-click="$filter == 'adc' ? $filter = 'all' : $filter = 'adc'" data-attr-selected="$filter == 'adc'">
            <img alt="supp" src="/static/img/supp.webp" data-on-click="$filter == 'sup' ? $filter = 'all' : $filter = 'sup'" data-attr-selected="$filter == 'sup'">
            <div></div>
            <input data-bind-search type="text" placeholder="Search"></input>
        </div>
        <div id="legends" data-on-click="@post('/d/{draft_id}?pick=' + event.target.id)">
            {"".join(
                [
                    f'''
                    <div 
                    id="{key}" 
                    data-sheet={champ['sheet']}
                    data-champion="{champ['name']}"
                    aria-describedby="aria-{champ['name']}" 
                    data-show="($filter == 'all' || $filter == {'|| $filter == '.join(f"'{role}'" for role in champ['role'])}) 
                    && ($search == '' || '{champ['name']}'.toLowerCase().includes($search.toLowerCase()))">'''
                    + f'<div id=aria-{champ['name']} role="tooltip">{champ['name']}</div></div>'
                    for key, champ in champs.items()
                ]
            )}
        </div>
    </article>
    <article id ="red-side" class="gc">
        <div data-sheet={champs.get(draft.r1p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r1p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r2p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r2p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r3p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r3p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r4p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r4p, the_chefs_trick)['name']}"></div>
        <div data-sheet={champs.get(draft.r5p, the_chefs_trick)['sheet']} data-champion="{champs.get(draft.r5p, the_chefs_trick)['name']}"></div>
    </article>
</div>
</body>
'''
    return html