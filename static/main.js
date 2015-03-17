function loadStuff(path) {
      $.get(path, function(response) {
        $("#info").html(response);
        if (path == '/get_flights'){
            loadFlights();
        }
        setDashboard();
      });
    }

function loadFlights() {
    // add in a try catch
      $.get("/flights.js", function(response) {
        try {
            window.pairs = JSON.parse(response);
        drawPairs();
        } catch(e) {
        }
      });
    }

function loadMethods(evt) {
    evt.preventDefault();
    $("#modal-wrapper").load("/static/carboncalcs.html", function () {
      $("#terms-modal").modal();
    });
  }

function setDashboard() {
    // console.log("setting dashboard");
    // console.log(carbonDebt);
    // console.log(typeof(carbonDebt));
    carbonPrice = ('$'+(carbonDebt*CO2ePrice).toFixed(2).toString());
    $("#carbon-debt").html(carbonDebt.toFixed(2));
    $("#carbon-price").html(carbonPrice);
    $("#donate").html('<button class="btn btn-lg btn-info" onclick="window.location.href=\'/donate?carbon_debt='+carbonPrice+'\'">Donate!</button>');
    }

function flightTotal() {
    // on getflights.html sums total number of flights in second table column
    var tdFlights = document.getElementsByClassName("flights");
    var fTotal = document.getElementById("fTotal");
    var fSum = 0;

    for (var i = 0; i < tdFlights.length; i++) {
        fSum += parseInt(tdFlights[i].getAttribute("data-amt"), 10);
    }

    fSum = fSum;
    fTotal.innerText = fSum;
}

function addTotals() {
    // Calculates and recalculates with user-edits the total carbon debt in metric tons and dollars
    var cTotal = document.getElementById("cTotal");
    var mTotal = document.getElementById("mTotal");
    var tdEmiss = document.getElementsByClassName("emiss");
    var tdPriced = document.getElementsByClassName("priced");
    var cSum = 0 ; mSum = 0;
    // console.log($(".emiss:eq(1)").html);

    for (var i = 0; i < tdEmiss.length; i++) {
        cSum += parseFloat(tdEmiss[i].getAttribute("data-amt"));
        mSum += parseFloat(tdPriced[i].getAttribute("data-amt"));
        }

    carbonDebt1 = cSum;
    cSum = cSum.toFixed(2);
    mSum = mSum.toFixed(2);
    mSum = mSum.toString();
    cTotal.innerText = cSum;
    mTotal.innerText = ("$" + mSum);
}

function drawPairs() {
    // Transform the short [lat,lng] format in our
    // data into the {x, y} expected by arc.js.
    
    if (! window.pairs){
        return;
    }

    function obj(ll) { return { y: ll[0], x: ll[1] }; }

    for (var i = 0; i < window.pairs.length; i++) {
        try {
            // Transform each pair of coordinates into a pretty
            // great circle using the Arc.js plugin, as included above.
            var generator = new arc.GreatCircle(
                    obj(window.pairs[i][0]),
                    obj(window.pairs[i][1]));
            var line = generator.Arc(100, { offset: 10 });

            var newLine = L.polyline(line.geometries[0].coords.map(function(c) {
                    return c.reverse();
            }), {
                color: '#40C0CB',
                weight: 2.5,
                opacity: 1
            })
            .addTo(map);

        } catch(e) {
            // coordinates are bad
            continue;
        }
        // Leaflet expects [lat,lng] arrays, but a lot of
        // software does the opposite, including arc.js, so
        // we flip here.
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
    }).setView([42, -100], 3);


    // Disable drag and zoom handlers.
    // Making this effect work with zooming and panning
    // would require a different technique with different
    // tradeoffs.
    // map.dragging.disable();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    if (map.tap) map.tap.disable();

    drawPairs();

});