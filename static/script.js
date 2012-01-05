var pattern_tiles, letter_tiles;

// jQuery and scriptaculous conflict
jQuery.noConflict();

// Document loaded
jQuery(document).ready(function(){
        initLetterTiles();
        initPatternTiles();
        });

function initPatternTiles()
{
    pattern_tiles = document.getElementsByName('pattern_tile');
    for(var i = 0; i < pattern_tiles.length; i++)
    {
        pattern_tiles[i].id = "pattern_tile_" + i;
        pattern_tiles[i].onmouseover = bind(previewGame, pattern_tiles[i], i+1);
        pattern_tiles[i].onmouseout = bind(previewGame, pattern_tiles[i], 0);
        pattern_tiles[i].onclick = bind(setupGame, pattern_tiles[i], i+1);
        Droppables.add(pattern_tiles[i].id, {onDrop: dropLetter});
    }
}

function initLetterTiles()
{
    letter_tiles = document.getElementsByName('letter_tile');
    for(var i = 0; i < letter_tiles.length; i++)
        letter_tiles[i].id = "letter_tile_" + letter_tiles[i].innerText;
}

function clearPatternTile(pattern_tile_id)
{
    var pattern_tile = document.getElementById(pattern_tile_id);
    var used = false;
    for(var i = 0; i < pattern_tiles.length; i++)
    {
        if(pattern_tiles[i].id !== pattern_tile.id && pattern_tiles[i].innerText === pattern_tile.innerText)
            used = true;
    }
    for(var i = 0; i < letter_tiles.length; i++)
    {
        if(letter_tiles[i].innerText === pattern_tile.innerText && used === false)
            letter_tiles[i].className = "filled_tile";
    }
    pattern_tile.innerText = "?";
    update();
}

function dropLetter(dragged, dropped, event)
{
    dropped.innerText = dragged.innerText;
    dragged.dropped = true;
    dragged.className = "correct_tile";
    update();
}

function bind(fnc, obj, arg)
{
    return function() {
        return fnc.apply(obj, [arg])
    }
}

function previewGame(letter_count)
{
    for(var i = 0; i < pattern_tiles.length; i++)
    {
        if(i < letter_count)
        {
            pattern_tiles[i].className = "filled_tile";
            pattern_tiles[i].innerText = "?";
        }
        else
        {
            pattern_tiles[i].className = "blank_tile";
            pattern_tiles[i].innerText = "";
        }
    }
}

function setupGame(letter_count)
{
    if(letter_count < 4)
        return;

    for(var i = 0; i < pattern_tiles.length; i++)
    {
        if(i < letter_count)
        {
            pattern_tiles[i].onclick = bind(clearPatternTile,
                    pattern_tiles[i], pattern_tiles[i].id);
        }
        else
        {
            pattern_tiles[i].onclick = null;
        }
        pattern_tiles[i].onmouseover = null;
        pattern_tiles[i].onmouseout = null;
    }
    enableLetterTiles();
}

function toggleUseLetter(letter_tile_id)
{
    var letter_tile = document.getElementById(letter_tile_id);
    if(letter_tile.dropped === true)
    {
        letter_tile.dropped = false;
        return;
    }

    if(letter_tile.className === "correct_tile")
    {
        letter_tile.className = "used_tile";
        for(var i = 0; i < pattern_tiles.length; i++)
        {
            if(pattern_tiles[i].innerText === letter_tile.innerText)
            {
                clearPatternTile(pattern_tiles[i].id);
            }
        }
    }
    else if(letter_tile.className === "filled_tile")
    {
        letter_tile.className = "used_tile";
    }
    else
    {
        letter_tile.className = "filled_tile";
    }

    update();
}

function disableLetterTiles()
{
    for(var i = 0; i < letter_tiles.length; i++)
    {
        letter_tiles[i].draggable.destroy();
    }
}

function touchToMouse(event)
{
    if(event.touches.length > 1) return;
    var touch = event.changedTouches[0];
    var type = "";
    switch(event.type)
    {
        case "touchstart":
            type = "mousedown"; break;
        case "touchmove":
            type = "mousemove"; break;
        case "touchend":
            type = "mouseup"; break;
        default: return;
    }
    var simulatedEvent = document.createEvent("MouseEvent");
    simulatedEvent.initMouseEvent(type, true, true, window, 1, touch.screenX, touch.screenY,
            touch.clientX, touch.clientY, false, false, false, false, 0, null);
    touch.target.dispatchEvent(simulatedEvent);
    if(type === "mouseup")
    {
        var simulatedEvent = document.createEvent("MouseEvent");
        simulatedEvent.initMouseEvent("click", true, true, window, 1, touch.screenX, touch.screenY,
                touch.clientX, touch.clientY, false, false, false, false, 0, null);
        touch.target.dispatchEvent(simulatedEvent);
    }
    event.preventDefault();
}

function enableLetterTiles()
{
    for(var i = 0; i < letter_tiles.length; i++)
    {
        letter_tiles[i].ontouchstart = touchToMouse;
        letter_tiles[i].ontouchmove = touchToMouse;
        letter_tiles[i].ontouchend = touchToMouse;
        letter_tiles[i].draggable = new Draggable(letter_tiles[i].id, {revert: true});
        letter_tiles[i].onclick = bind(toggleUseLetter, letter_tiles[i],
                letter_tiles[i].id);
    }
}

function update()
{
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        if(req.readyState === 4 && req.status === 200)
        {
            var json = eval(req.responseText);
            document.getElementById("best_guesses").innerHTML = json.best_guesses;
            document.getElementById("num_remaining_words").innerHTML = json.num_matches;
            document.getElementById("remaining_words").innerHTML = json.matches;
            document.getElementById("expected_strikes_left").innerHTML =
                json.expected_strikes_left;
        }
    }
    var pattern = "";
    for(var i = 0; i < pattern_tiles.length; i++)
    {
        pattern += pattern_tiles[i].innerText;
    }
    var used_letters = "";
    for(var i = 0; i < letter_tiles.length; i++)
    {
        if(letter_tiles[i].className === "used_tile")
            used_letters += letter_tiles[i].innerText;
    }
    req.open("GET", "solve/" + escape(pattern) + "/" + escape(used_letters), true);
    req.send();
}

