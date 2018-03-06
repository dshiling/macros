// TODO: match frontend style guide at least loosely

/*
Creates accordion style animation for macro cards. Toggles class that's called out in css. Not very elegant. Consider
refactor before prod.
*/

// TODO: make whole card animated on click

var acc = document.getElementsByClassName("button-wrap");

for (var i = 0; i < acc.length; i++) {
    acc[i].onclick = function () {
        this.classList.toggle("active");
        var description = this.nextElementSibling;
        if (description.style.maxHeight) {
            description.style.maxHeight = null;
        } else {
            description.style.maxHeight = description.scrollHeight + "px";
        }
    }
}

/*
This method uses clipboard.js to copy text on button press and changes button text briefly before resetting.
Tooltips were a pita, this was way easier. Don't touch, works great.
*/

// Fixme: add clipboard.js to dev dependencies
// Fixme: don't load macro content twice for data-clipboard-text and for p tag.

var btns = document.querySelectorAll('.copy-btn');
var clipboard = new Clipboard(btns);


clipboard.on('success', function(e) {
    e.trigger.innerHTML = "Copied!";
    setTimeout(function () {
        e.trigger.innerHTML = "<img class='clippy' src='/static/img/clippy.svg'>";
    }, 2000);
});

clipboard.on('error', function(e) {
    e.trigger.innerHTML = "Error!";
    setTimeout(function () {
        e.trigger.innerHTML = "<img class='clippy' src='/static/img/clippy.svg'>";
    }, 2000);
});
