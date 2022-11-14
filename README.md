# bpgwrapper
A better pygame wrapper (better than the last one I made, at least).

This is an unfinished project of mine that I started working on mid-July, and stopped at the beggining of August (yes, I gave up quite quickly). This is a rewrite of a rewrite of the internals used for [my smart rockets project](https://github.com/BetaKors/smart-rockets), which was inspired by [p5.js](https://p5js.org), and [this video](https://www.youtube.com/watch?v=bGz7mv2vD6g) by [The Coding Train](https://www.youtube.com/c/TheCodingTrain). I guess you could say I actually started working on this around March, since that was when I worked on the smart rockets thingy, and this project and its predecessors were based on it.

This project has around 1600 LOC, and is one of my biggest ones so far. The rewrite prior to this one had quite a bit more documentation, having around 2200 LOC, and a more p5.js-like approach to rendering. This one has a bit of a different take on rendering since it uses objects to store the information about what to render and how to render it, instead of simply rendering things instantly whenever a certain function is called. Is that a good change? No clue, but I wanted to try something different, so I did.

I learned a whole lot about Python and mainly typing-related stuff, and it was a very fun project to work on (except when I had to deal with pygame being garbage, such as getting antialiasing to work being very hard).

(also btw fullscreen doesn't work on linux cuz I focused too much on fixing it for windows and forgot to add a case for linux)
(actually I'm not even sure if this whole thing works on linux at all)
