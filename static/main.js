function loadStuff(path) {
      $.get(path, function(response) {
        $("#info").html(response);
        console.log(carbonDebt);
        $("#carbon-debt").html(carbonDebt);
        $("#carbon-price").html(carbonDebt*carbonPrice);
      });
    }

function loadMethods(evt) {
    evt.preventDefault();
    $("#modal-wrapper").load("/static/carboncalcs.html", function () {
      $("#terms-modal").modal();
    });
  }

$(document).ready(function(){
    $("#load-methods").on("click", loadMethods);
    // Intercept clicks of anchor tags
    $('#info').on('click', 'a', function(ev) {
        var ogHref = ev.target.href;
        loadStuff(ogHref);
        ev.preventDefault();
    });

    // MAPBOX SCRIPT
      L.mapbox.accessToken = 'pk.eyJ1IjoidGF5Z3JhdmUiLCJhIjoiTC02ZVBocyJ9.v07HDiBCNqymCU6IsCF1jQ';
    // This is an advanced example that is compatible with
    // modern browsers and IE9+ - the trick it uses is animation
    // of SVG properties, which makes it relatively efficient for
    // the effect produced. That said, the same trick means that the
    // animation is non-geographical - lines interpolate in the same
    // amount of time regardless of trip length.

    // Show the whole world in this first view.
    map = L.mapbox.map('map', 'taygrave.lc074chc', {
      zoomControl: false
    }).setView([42, -100], 4);


    // Disable drag and zoom handlers.
    // Making this effect work with zooming and panning
    // would require a different technique with different
    // tradeoffs.
    // map.dragging.disable();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    if (map.tap) map.tap.disable();

    // Transform the short [lat,lng] format in our
    // data into the {x, y} expected by arc.js.
    function obj(ll) { return { y: ll[0], x: ll[1] }; }

    for (var i = 0; i < pairs.length; i++) {
        // Transform each pair of coordinates into a pretty
        // great circle using the Arc.js plugin, as included above.
        var generator = new arc.GreatCircle(
                obj(pairs[i][0]),
                obj(pairs[i][1]));
        var line = generator.Arc(100, { offset: 10 });
        // Leaflet expects [lat,lng] arrays, but a lot of
        // software does the opposite, including arc.js, so
        // we flip here.
        var newLine = L.polyline(line.geometries[0].coords.map(function(c) {
            return c.reverse();
        }), {
            color: '#66cd00',
            weight: 2,
            opacity: 0.5
        })
        .addTo(map);
        var totalLength = newLine._path.getTotalLength();
        newLine._path.classList.add('path-start');
        // This pair of CSS properties hides the line initially
        // See http://css-tricks.com/svg-line-animation-works/
        // for details on this trick.
        newLine._path.style.strokeDashoffset = totalLength;
        newLine._path.style.strokeDasharray = totalLength;
        // Offset the timeout here: setTimeout makes a function
        // run after a certain number of milliseconds - in this
        // case we want each flight path to be staggered a bit.
        setTimeout((function(path) {
            return function() {
                // setting the strokeDashoffset to 0 triggers
                // the animation.
                path.style.strokeDashoffset = 0;
            };
        })(newLine._path), i * 100);
    }


});